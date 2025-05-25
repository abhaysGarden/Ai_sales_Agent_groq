def compute_llm_score(metrics: dict, weights: dict = None) -> float:
    """Compute the overall LLM evaluation score from the individual metrics.

    This is a simple weighted average of the following metrics:

    - intent_f1: how well do the predicted intents match the gold standard?
    - entity_f1: how well do the predicted entities match the gold standard?
    - response_similarity: how similar is the predicted response to the gold standard?
    - tool_call_score: how well do the predicted tool calls match the gold standard?
    - confidence_score: how confident is the model in its predictions?

    The weights are hardcoded as 0.2 for each metric, so the overall score is a simple average.
    """
    
    default_weights = {
        "intent_f1": 0.2,
        "entity_f1": 0.2,
        "response_similarity": 0.2,
        "tool_call_score": 0.2,
        "confidence_score": 0.2,
    }
    w = weights or default_weights

    score = sum(metrics.get(k, 0) * w.get(k, 0) for k in w)
    return round(score, 4)