from fastapi import APIRouter, HTTPException
from app.models.schemas import ProcessMessageRequest, ProcessMessageResponse
from app.core.llm_orchestrator import process_message_pipeline

router = APIRouter()


@router.post("/process_message", response_model=ProcessMessageResponse)
async def process_message(request: ProcessMessageRequest):
    """
    Process a message from a prospect.

    This endpoint takes a ProcessMessageRequest as input and returns a ProcessMessageResponse.
    The request contains the conversation history and current message from the prospect.
    The response contains the suggested response draft, internal next steps, confidence scores, tool usage logs, and reasoning trace.

    Args:
        request (ProcessMessageRequest): The request containing the conversation history and current message.

    Returns:
        ProcessMessageResponse: The response containing the suggested response draft, internal next steps, confidence scores, tool usage logs, and reasoning trace.

    Raises:
        HTTPException: If there is an internal server error.
    """
    try:
        result = await process_message_pipeline(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
