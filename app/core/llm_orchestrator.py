import os
import json
import asyncio
from typing import List
from groq import AsyncGroq
from dotenv import load_dotenv
from app.models.schemas import (
    Message, ProcessMessageRequest, ProcessMessageResponse,
    AnalysisResult, ToolUsageLogEntry
)
from app.core.tools import KnowledgeAugmentationTool

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
model_name = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
temperature = float(os.getenv("GROQ_TEMPERATURE", "0.3"))


class LLMOrchestrator:
    def __init__(self):
        self.tool = KnowledgeAugmentationTool()

    async def analyze_message(self, request: ProcessMessageRequest) -> AnalysisResult:
        prompt = f"""
You are a sales assistant AI. Analyze the following message in the context of the conversation history.
Identify the user's intent, sentiment, and any product-related entities.

CONVERSATION HISTORY:
{self._format_history(request.conversation_history)}

CURRENT MESSAGE:
"{request.current_prospect_message}"

Return in JSON format:
{{
    "intent": "...",
    "sentiment": "...",
    "entities": [...],
    "confidence": 0.0 - 1.0
}}
"""
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        analysis_json = json.loads(response.choices[0].message.content)
        return AnalysisResult(**analysis_json)

    async def process(self, request: ProcessMessageRequest) -> ProcessMessageResponse:
        analysis = await self.analyze_message(request)

        tool_usage_log = []
        retrieved_knowledge = []

        if request.prospect_id:
            crm_data = self.tool.fetch_prospect_details(request.prospect_id)
            tool_usage_log.append(ToolUsageLogEntry(
                tool_name="KnowledgeAugmentationTool",
                function="fetch_prospect_details",
                input={"prospect_id": request.prospect_id},
                output_summary=str(crm_data)
            ))
            retrieved_knowledge.append(f"CRM Data: {crm_data}")

        if analysis.intent in ["objection", "clarification", "inquiry"]:
            query_text = f"{request.current_prospect_message} | Entities: {', '.join(analysis.entities)}"
            kb_result = self.tool.query_knowledge_base(query_text)
            tool_usage_log.append(ToolUsageLogEntry(
                tool_name="KnowledgeAugmentationTool",
                function="query_knowledge_base",
                input={"query": query_text},
                output_summary="; ".join([doc['text'][:200] for doc in kb_result])
            ))
            retrieved_knowledge.append("Knowledge Base Results:\n" + "\n".join([doc["text"] for doc in kb_result]))

        final_response = await self.synthesize_response(request, analysis, retrieved_knowledge)

        return ProcessMessageResponse(
            detailed_analysis=analysis,
            suggested_response_draft=final_response["response"],
            internal_next_steps=final_response["next_steps"],
            confidence_score=analysis.confidence,
            tool_usage_log=tool_usage_log,
            reasoning_trace=final_response.get("reasoning_trace", "")
        )

    async def synthesize_response(self, request, analysis, knowledge_blocks) -> dict:
        prompt = f"""
You're an AI sales assistant helping draft the next message to a prospect.

CONVERSATION HISTORY:
{self._format_history(request.conversation_history)}

CURRENT MESSAGE:
"{request.current_prospect_message}"

ANALYSIS:
Intent: {analysis.intent}
Sentiment: {analysis.sentiment}
Entities: {analysis.entities}

RETRIEVED KNOWLEDGE:
{chr(10).join(knowledge_blocks)}

TASK:
- Write a clear, concise, helpful response to the prospect.
- Recommend internal next steps as a JSON list. Use only these exact values for `action`:
  - UPDATE_CRM
  - SCHEDULE_FOLLOW_UP
  - FLAG_FOR_HUMAN_REVIEW
  - NO_ACTION
- Explain your reasoning.

Output in JSON:
{{
  "response": "string",
  "next_steps": [
    {{
      "action": "SCHEDULE_FOLLOW_UP",
      "details": {{
        "when": "next Tuesday",
        "reason": "Prospect showed interest but asked for more info"
      }}
    }}
  ],
  "reasoning_trace": "Prospect asked about pricing, which indicates interest. Following up is recommended."
}}
"""
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        content = response.choices[0].message.content
        return json.loads(content)

    def _format_history(self, history: List[Message]) -> str:
        return "\n".join([f"[{msg.timestamp}] {msg.sender}: {msg.content}" for msg in history])


orchestrator = LLMOrchestrator()

def process_message_pipeline(request: ProcessMessageRequest) -> ProcessMessageResponse:
    return asyncio.run(orchestrator.process(request))
