import os
import json
from openai import AsyncOpenAI
from typing import List
from app.models.schemas import (
    Message, ProcessMessageRequest, ProcessMessageResponse,
    AnalysisResult, ToolUsageLogEntry
)
from app.core.tools import KnowledgeAugmentationTool
from dotenv import load_dotenv
load_dotenv()

# Use environment variable or placeholder

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model_name = os.getenv("OPENAI_MODEL", "gpt-4")           
temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))



class LLMOrchestrator:
    def __init__(self):
        """
        Initialize the LLMOrchestrator with a KnowledgeAugmentationTool instance.

        The tool is used for CRM lookups and knowledge base queries to support
        the orchestration process.
        """

        self.tool = KnowledgeAugmentationTool()

    async def analyze_message(self, request: ProcessMessageRequest) -> AnalysisResult:
        """
        Analyze the given message in the context of the conversation history.

        Asks an OpenAI GPT model to analyze the message and identify the user's intent, sentiment, and any product-related entities.

        Args:
            request (ProcessMessageRequest): The request containing the conversation history and current message.

        Returns:
            AnalysisResult: The analysis result as a named tuple with the intent, sentiment, entities, and confidence.
        """

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
        """
        Process a message from a prospect and return a ProcessMessageResponse.

        ProcessMessageResponse includes the analysis of the message, a suggested response draft, internal next steps, confidence scores, tool usage logs, and the reasoning trace.

        The process is as follows:

        1. Analyze the message using an OpenAI GPT model.
        2. If the message is an objection, clarification, or inquiry, query the knowledge base.
        3. If the prospect_id is present, perform a CRM lookup.
        4. Synthesize a response using the knowledge retrieved and the analysis.

        Args:
            request (ProcessMessageRequest): The request containing the conversation history and current message.

        Returns:
            ProcessMessageResponse: The ProcessMessageResponse containing the analysis, suggested response draft, internal next steps, confidence scores, tool usage logs, and reasoning trace.
        """
        analysis = await self.analyze_message(request)

        tool_usage_log = []
        retrieved_knowledge = []

        # CRM Lookup if prospect_id is present
        if request.prospect_id:
            crm_data = self.tool.fetch_prospect_details(request.prospect_id)
            tool_usage_log.append(ToolUsageLogEntry(
                tool_name="KnowledgeAugmentationTool",
                function="fetch_prospect_details",
                input={"prospect_id": request.prospect_id},
                output_summary=str(crm_data)
            ))
            retrieved_knowledge.append(f"CRM Data: {crm_data}")

        # RAG Query if entities or objection present
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

        # Synthesize response
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
        """
        Synthesize a response using the knowledge retrieved and the analysis.

        Args:
            request (ProcessMessageRequest): The request containing the conversation history and current message.
            analysis (AnalysisResult): The AnalysisResult of the message.
            knowledge_blocks (List[str]): The retrieved knowledge relevant to the message.

        Returns:
            dict: A dictionary containing the suggested response draft, internal next steps, and reasoning trace.
        """

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
        """
        Format a list of Messages into a string.

        The string is formatted as follows:

        [timestamp] sender: content

        where timestamp is the timestamp of the message in ISO format,
        sender is the sender of the message, and content is the content of the message.

        Args:
            history (List[Message]): The list of messages to format.

        Returns:
            str: The formatted string.
        """
        return "\n".join([f"[{msg.timestamp}] {msg.sender}: {msg.content}" for msg in history])

orchestrator = LLMOrchestrator()

async def process_message_pipeline(request: ProcessMessageRequest) -> ProcessMessageResponse:
    """
    Process a message from a prospect.

    This pipeline is the entry point into the LLM Orchestrator. It takes a ProcessMessageRequest
    as input, containing the conversation history and current message from the prospect.

    The pipeline processes the message by:

    1. Analyzing the message to identify its intent, sentiment, and any relevant entities.
    2. Deciding if any external tools should be called (e.g. CRM lookup, RAG query).
    3. Executing the necessary tool calls.
    4. Synthesizing a response draft using the retrieved knowledge and analysis.
    5. Returning a ProcessMessageResponse containing the suggested response draft, internal next steps, tool usage logs, and confidence scores.

    Args:
        request (ProcessMessageRequest): The request containing the conversation history and current message.

    Returns:
        ProcessMessageResponse: The response containing the suggested response draft, internal next steps, tool usage logs, and confidence scores.
    """
    return await orchestrator.process(request)

    