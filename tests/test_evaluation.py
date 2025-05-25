import pytest
from app.evaluation import evaluate_lite, evaluate_full


# Sample golden dataset entry with perfect match
perfect_entry = {
    "id": "001",
    "conversation_history": [
        {"sender": "user", "content": "Hi, I'm interested in pricing."}
    ],
    "current_prospect_message": "Can you share the pricing options?",
    "prospect_id": "P001",
    "ground_truth": {
        "intent": "pricing_inquiry",
        "entities": ["pricing", "options"],
        "tools_to_call": ["crm_lookup"],
        "suggested_response_draft": "Sure, I can share our pricing options.",
        "internal_next_steps": ["log_inquiry"]
    },
    "predicted": {
        "intent": "pricing_inquiry",
        "entities": ["pricing", "options"],
        "tools_to_call": ["crm_lookup"],
        "suggested_response_draft": "Sure, I can share our pricing options.",
        "internal_next_steps": ["log_inquiry"]
    }
}

# Sample entry with mismatched intent and partial entity match
imperfect_entry = {
    "id": "002",
    "conversation_history": [
        {"sender": "user", "content": "Tell me about premium plans."}
    ],
    "current_prospect_message": "What are your premium options?",
    "prospect_id": "P002",
    "ground_truth": {
        "intent": "plan_inquiry",
        "entities": ["premium", "plans"],
        "tools_to_call": [],
        "suggested_response_draft": "We have multiple premium plans.",
        "internal_next_steps": []
    },
    "predicted": {
        "intent": "general_inquiry",
        "entities": ["plans"],
        "tools_to_call": [],
        "suggested_response_draft": "We have multiple premium plans.",
        "internal_next_steps": []
    }
}

@pytest.mark.parametrize("entry,expected", [
    ([perfect_entry], {
        "intent_accuracy": 1.0,
        "entity_f1_score": 1.0,
        "response_match_accuracy": 1.0
    }),
    ([imperfect_entry], {
        "intent_accuracy": 0.0,
        "entity_f1_score": 0.6666,  # F1 for ['premium', 'plans'] vs ['plans']
        "response_match_accuracy": 1.0
    }),
])
def test_evaluate_lite(entry, expected):
    """Test evaluation_lite function on a list of perfect and imperfect entries.
    The perfect entry should have all metrics at 1.0, while the imperfect entry
    will have intent accuracy at 0.0 and entity F1 score of 2/3. The response
    match accuracy is at 1.0 for both since the generated response is the same.
    """

    result = evaluate_lite(entry)
    assert pytest.approx(result["intent_accuracy"], 0.01) == expected["intent_accuracy"]
    assert pytest.approx(result["entity_f1_score"], 0.01) == expected["entity_f1_score"]
    assert pytest.approx(result["response_match_accuracy"], 0.01) == expected["response_match_accuracy"]

def test_evaluate_full_structure():
    """Test evaluate_full function returns a dictionary with all expected keys and their corresponding values as floats."""
    result = evaluate_full([perfect_entry])
    keys = [
        "intent_accuracy",
        "entity_f1_score",
        "response_match_accuracy",
        "tools_accuracy",
        "steps_accuracy"
    ]
    for key in keys:
        assert key in result
        assert isinstance(result[key], float)
