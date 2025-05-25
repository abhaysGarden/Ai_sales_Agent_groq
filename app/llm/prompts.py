def orchestration_prompt_v1(conversation_history, current_message, prospect_id):
    
    """
    A very direct prompt version of the orchestration prompt.
    """
    
    return {
        "intent": "pricing_comparison",
        "entities": ["enterprise plan", "pro plan"],
        "suggested_response_draft": "Sure! The enterprise plan includes advanced analytics...",
        "tool_calls": ["query_knowledge_base"],
        "confidence_score": 0.85  
    }


def orchestration_prompt_v2(conversation_history, current_message, prospect_id):
    """
    A more verbose, chain-of-thought reasoning version of the orchestration prompt.
    """
    return {
        "intent": "pricing_comparison",
        "entities": ["enterprise plan", "pro plan"],
        "suggested_response_draft": "To help you understand the difference, here’s a quick summary...",
        "tool_calls": ["query_knowledge_base"],
        "confidence_score": 0.92  
    }
