from difflib import SequenceMatcher
from typing import List

def compute_intent_f1(pred_intent: str, true_intent: str):
    """Return 1 if the predicted and true intents match, 0 otherwise."""
    return int(pred_intent == true_intent)

def compute_entity_overlap(pred_entities: List[str], true_entities: List[str]):
    """
    Compute precision, recall, and F1 score for predicted vs true entities.

    Args:
        pred_entities: List of predicted entity strings.
        true_entities: List of true entity strings.

    Returns:
        A dictionary containing precision, recall, and F1 score.
    """

    pred_set, true_set = set(pred_entities), set(true_entities)
    intersection = pred_set & true_set
    precision = len(intersection) / len(pred_set) if pred_set else 0
    recall = len(intersection) / len(true_set) if true_set else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    return {"precision": precision, "recall": recall, "f1": f1}

def similarity_score(a: str, b: str) -> float:
    """Compute a similarity score between two strings.

    The similarity score is a float in [0.0, 1.0] indicating the degree of similarity
    between the two strings. The score is computed as the size of the longest common
    subsequence divided by the maximum of the sizes of the two strings.

    Args:
        a (str): The first string.
        b (str): The second string.

    Returns:
        float: The similarity score between the two strings, from 0 (completely dissimilar)
            to 1 (completely identical).
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
