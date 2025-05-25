def track_kpis(logged_events: list) -> dict:
    """
    Calculates key performance indicators from a list of logged events.

    Args:
        logged_events (list): A list of dictionaries where each dictionary represents an event and may contain
                            keys such as 'confidence_score', 'latency_ms', 'tool_error', and 'action'.

    Returns:
        dict: A dictionary containing the following KPIs:
            - 'avg_confidence': The average confidence score across all events.
            - 'tool_error_rate': The proportion of events that have a tool error.
            - 'avg_latency': The average latency in milliseconds across all events.
            - 'flag_rate': The proportion of events flagged for human review.
    """

    total = len(logged_events)
    if total == 0:
        return {}

    return {
        "avg_confidence": sum(e.get("confidence_score", 0) for e in logged_events) / total,
        "tool_error_rate": sum(1 for e in logged_events if e.get("tool_error")) / total,
        "avg_latency": sum(e.get("latency_ms", 0) for e in logged_events) / total,
        "flag_rate": sum(1 for e in logged_events if e.get("action") == "FLAG_FOR_HUMAN_REVIEW") / total
    }