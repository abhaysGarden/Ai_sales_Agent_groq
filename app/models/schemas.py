from typing import List, Optional, Literal
from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    sender: Literal["prospect", "agent"]
    content: str
    timestamp: datetime


class ProcessMessageRequest(BaseModel):
    conversation_history: List[Message]
    current_prospect_message: str
    prospect_id: Optional[str] = None


class ToolUsageLogEntry(BaseModel):
    tool_name: str
    function: str
    input: dict
    output_summary: str


class InternalAction(BaseModel):
    action: Literal[
        "UPDATE_CRM", "SCHEDULE_FOLLOW_UP", "FLAG_FOR_HUMAN_REVIEW", "NO_ACTION"
    ]
    details: Optional[dict]


class AnalysisResult(BaseModel):
    intent: str
    entities: List[str]
    sentiment: str
    confidence: float


class ProcessMessageResponse(BaseModel):
    detailed_analysis: AnalysisResult
    suggested_response_draft: str
    internal_next_steps: List[InternalAction]
    tool_usage_log: List[ToolUsageLogEntry]
    confidence_score: float
    reasoning_trace: Optional[str] = None
