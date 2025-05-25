import json
import argparse
from typing import List, Dict
import logging

try:
    from sklearn.metrics import classification_report
except ImportError:
    classification_report = None

try:
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
except ImportError:
    sentence_bleu = None

logger = logging.getLogger(__name__)

# Optional: Import only if using full mode
try:
    from sklearn.metrics import classification_report
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
except ImportError:
    classification_report = None
    sentence_bleu = None

def entity_f1(gt_entities: List[str], pred_entities: List[str]) -> float:
    """
    Compute the F1 score for a single example's entity recognition.

    Args:
        gt_entities: List of ground truth entity strings.
        pred_entities: List of predicted entity strings.

    Returns:
        The F1 score of the prediction.
    """
    gt_set = set(gt_entities)
    pred_set = set(pred_entities)
    if not gt_set and not pred_set:
        return 1.0
    if not gt_set or not pred_set:
        return 0.0
    tp = len(gt_set & pred_set)
    prec = tp / len(pred_set)
    rec = tp / len(gt_set)
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)

def compute_bleu(reference: str, hypothesis: str) -> float:
    """
    Compute the BLEU score for a single example's response draft.

    Args:
        reference: The ground truth response draft.
        hypothesis: The predicted response draft.

    Returns:
        The BLEU score of the prediction, or -1 if BLEU is not installed.
    """
    # BLEU not available
    if not sentence_bleu:
        return -1  
    # Use smoothing to avoid zero score on short sentences
    smoothie = SmoothingFunction().method4
    return sentence_bleu([reference.split()], hypothesis.split(), smoothing_function=smoothie)

def evaluate_lite(dataset: List[Dict], print_report: bool = False) -> Dict[str, float]:
    """
    Evaluate a list of dictionaries with ground truth and predicted fields.

    Args:
        dataset: List of dictionaries with ground truth and predicted fields.
        print_report: Whether to print a classification report.

    Returns:
        A dictionary with the following metrics:

        - intent_accuracy: Accuracy of the intent prediction.
        - entity_f1_score: Average F1 score of the entity prediction.
        - response_bleu_score: Average BLEU score of the suggested response draft prediction.
    """
    intent_true = []
    intent_pred = []
    entity_f1_scores = []
    response_bleu_scores = []

    for entry in dataset:
        gt = entry["ground_truth"]
        pred = entry["predicted"]

        # Collect intents for classification report
        intent_true.append(gt.get("intent", ""))
        intent_pred.append(pred.get("intent", ""))

        # Entity F1
        f1 = entity_f1(gt.get("entities", []), pred.get("entities", []))
        entity_f1_scores.append(f1)

        # BLEU for suggested response draft (if text present)
        gt_resp = gt.get("suggested_response_draft", "")
        pred_resp = pred.get("suggested_response_draft", "")
        bleu = compute_bleu(gt_resp, pred_resp) if gt_resp and pred_resp else 1.0 if gt_resp == pred_resp else 0.0
        response_bleu_scores.append(bleu)

    intent_accuracy = sum(1 for t, p in zip(intent_true, intent_pred) if t == p) / len(intent_true) if intent_true else 0.0
    avg_entity_f1 = sum(entity_f1_scores) / len(entity_f1_scores) if entity_f1_scores else 0.0
    # Filter out BLEU -1 (missing)
    valid_bleu_scores = [b for b in response_bleu_scores if b >= 0]
    avg_bleu = sum(valid_bleu_scores) / len(valid_bleu_scores) if valid_bleu_scores else 0.0

    if print_report and classification_report:
        logger.info("\nIntent Classification Report:")
        logger.info(classification_report(intent_true, intent_pred, zero_division=0))

    return {
        "intent_accuracy": intent_accuracy,
        "entity_f1_score": avg_entity_f1,
        "response_bleu_score": avg_bleu,
    }

def evaluate_full(dataset: List[Dict], print_report: bool = False) -> Dict[str, float]:
    """
    Evaluate a dataset of predicted vs ground truth with additional metrics on tools to call and internal next steps.

    Args:
        dataset (List[Dict]): A list of dictionary entries, each containing "ground_truth" and "predicted".
        print_report (bool, optional): Whether to print the detailed evaluation report. Defaults to False.

    Returns:
        Dict[str, float]: A dictionary containing the evaluation metrics, including intent accuracy, entity F1, response BLEU, tools accuracy, and internal next steps accuracy.
    """
    lite_metrics = evaluate_lite(dataset, print_report=print_report)

    total = len(dataset)
    tools_correct = 0
    steps_correct = 0

    for entry in dataset:
        gt = entry["ground_truth"]
        pred = entry["predicted"]

        # Tools exact match (ignore order)
        if sorted(gt.get("tools_to_call", [])) == sorted(pred.get("tools_to_call", [])):
            tools_correct += 1

        # Internal next steps exact match (ignore order)
        if sorted(gt.get("internal_next_steps", [])) == sorted(pred.get("internal_next_steps", [])):
            steps_correct += 1

    tools_accuracy = tools_correct / total if total else 0.0
    steps_accuracy = steps_correct / total if total else 0.0

    if print_report:
        logger.info(f"\nTools Accuracy: {tools_accuracy:.3f}")
        logger.info(f"Internal Next Steps Accuracy: {steps_accuracy:.3f}")

    return {
        **lite_metrics,
        "tools_accuracy": tools_accuracy,
        "steps_accuracy": steps_accuracy,
    }


def semantic_similarity(a: str, b: str) -> float:
    """Compute the semantic similarity between two strings using the SequenceMatcher's ratio method.

    This measures the longest common subsequence between the two strings, and returns a
    score from 0 (completely dissimilar) to 1 (completely identical). The score is
    computed as the size of the longest common subsequence divided by the maximum of the
    sizes of the two strings.

    Args:
        a (str): The first string.
        b (str): The second string.

    Returns:
        float: The semantic similarity between the two strings, from 0 (completely dissimilar)
            to 1 (completely identical).
    """
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()


def entity_overlap(predicted: List[str], expected: List[str]) -> float:
    """
    Compute the overlap between two lists of strings as a similarity score.
    
    If the expected list is empty, returns 1.0 if the predicted list is also empty, 0.0 otherwise.
    
    Otherwise, returns the ratio of the intersection of the two sets to the size of the expected set.
    
    :param predicted: The list of strings predicted by the model.
    :param expected: The list of strings expected as ground truth.
    :return: A float in [0.0, 1.0] indicating the degree of overlap.
    """
    predicted_set = set([e.lower() for e in predicted])
    expected_set = set([e.lower() for e in expected])
    if not expected_set:
        return 1.0 if not predicted_set else 0.0
    return len(predicted_set & expected_set) / len(expected_set)


def tool_call_match(predicted: List[str], expected: List[str]) -> float:
    """
    Compute the similarity between two lists of strings as a tool call match score.
    
    If the expected list is empty, returns 1.0 if the predicted list is also empty, 0.0 otherwise.
    
    Otherwise, returns the ratio of the intersection of the two sets to the size of the expected set.
    
    :param predicted: The list of strings predicted by the model.
    :param expected: The list of strings expected as ground truth.
    :return: A float in [0.0, 1.0] indicating the degree of tool call match.
    """
    pred_set = set(predicted)
    exp_set = set(expected)
    if not exp_set:
        return 1.0 if not pred_set else 0.0
    return len(pred_set & exp_set) / len(exp_set)



def evaluate_lite(dataset: List[Dict]) -> Dict[str, float]:
    """
    Light evaluation on a dataset list with predicted vs ground truth.
    Computes simple metrics like intent accuracy, entity F1, and response match.
    """
    intent_correct = 0
    total = len(dataset)
    entity_precisions = []
    entity_recalls = []
    response_match_count = 0

    for entry in dataset:
        gt = entry["ground_truth"]
        pred = entry["predicted"]

        # Intent accuracy
        if gt["intent"] == pred["intent"]:
            intent_correct += 1

        # Entities precision, recall, F1
        gt_entities = set(gt.get("entities", []))
        pred_entities = set(pred.get("entities", []))

        if gt_entities or pred_entities:
            tp = len(gt_entities & pred_entities)
            prec = tp / len(pred_entities) if pred_entities else 0.0
            rec = tp / len(gt_entities) if gt_entities else 0.0
            entity_precisions.append(prec)
            entity_recalls.append(rec)
        else:
            # If no entities in both, count as perfect match
            entity_precisions.append(1.0)
            entity_recalls.append(1.0)

        # Suggested response draft exact match
        if gt.get("suggested_response_draft", "") == pred.get("suggested_response_draft", ""):
            response_match_count += 1

    # Compute averages
    avg_prec = sum(entity_precisions) / total if total else 0
    avg_rec = sum(entity_recalls) / total if total else 0
    if avg_prec + avg_rec > 0:
        entity_f1 = 2 * avg_prec * avg_rec / (avg_prec + avg_rec)
    else:
        entity_f1 = 0.0

    return {
        "intent_accuracy": intent_correct / total if total else 0.0,
        "entity_f1_score": entity_f1,
        "response_match_accuracy": response_match_count / total if total else 0.0
    }

def evaluate_full(dataset: List[Dict]) -> Dict[str, float]:
    """
    Full evaluation including tools and next steps accuracy,
    plus the metrics in evaluate_lite.
    """
    lite_metrics = evaluate_lite(dataset)

    total = len(dataset)
    tools_correct = 0
    steps_correct = 0

    for entry in dataset:
        gt = entry["ground_truth"]
        pred = entry["predicted"]

        # Tools accuracy: exact match of tool list
        if sorted(gt.get("tools_to_call", [])) == sorted(pred.get("tools_to_call", [])):
            tools_correct += 1

        # Internal next steps accuracy: exact match of list
        if sorted(gt.get("internal_next_steps", [])) == sorted(pred.get("internal_next_steps", [])):
            steps_correct += 1

    return {
        **lite_metrics,
        "tools_accuracy": tools_correct / total if total else 0.0,
        "steps_accuracy": steps_correct / total if total else 0.0,
    }


# def evaluate_lite(example: Dict) -> Dict:
#     predicted = example["predicted"]
#     expected = example["expected"]

#     return {
#         "intent_match": int(predicted["intent"] == expected["intent"]),
#         "entity_accuracy": entity_overlap(predicted["entities"], expected["entities"]),
#         "tool_call_score": tool_call_match(predicted["tool_calls"], expected["tool_calls"]),
#         "response_similarity": semantic_similarity(
#             predicted["suggested_response_draft"], expected["suggested_response_draft"]
#         ),
#         "confidence_score": predicted.get("confidence_score", 0.0),
#     }


def calculate_llm_score(metrics: Dict) -> float:
    """
    Calculate the overall LLM evaluation score from the individual metrics.

    This is a simple weighted average of the following metrics:

    - intent_match: whether the predicted intent matches the gold standard
    - entity_accuracy: how well do the predicted entities match the gold standard?
    - tool_call_score: how well do the predicted tool calls match the gold standard?
    - response_similarity: how similar is the predicted response to the gold standard?
    - confidence_score: how confident is the model in its predictions?

    The weights are hardcoded as 0.2 for each metric, so the overall score is a simple average.
    """
    return round(
        0.2 * metrics["intent_match"]
        + 0.2 * metrics["entity_accuracy"]
        + 0.2 * metrics["tool_call_score"]
        + 0.2 * metrics["response_similarity"]
        + 0.2 * metrics["confidence_score"], 4
    )


# def evaluate_full(dataset: List[Dict]) -> None:
#     if not classification_report or not sentence_bleu:
#         print("Full evaluation requires scikit-learn and nltk. Install with: pip install scikit-learn nltk")
#         return

#     intents_gold = []
#     intents_pred = []
#     entity_f1_list = []
#     tool_f1_list = []
#     bleu_scores = []

#     for ex in dataset:
#         pred = ex["predicted"]
#         gold = ex["expected"]

#         # Intent
#         intents_gold.append(gold["intent"])
#         intents_pred.append(pred["intent"])

#         # Entity
#         entity_f1_list.append(entity_overlap(pred["entities"], gold["entities"]))

#         # Tool
#         tool_f1_list.append(tool_call_match(pred["tool_calls"], gold["tool_calls"]))

#         # BLEU
#         ref = [gold["suggested_response_draft"].split()]
#         hyp = pred["suggested_response_draft"].split()
#         bleu = sentence_bleu(ref, hyp, smoothing_function=SmoothingFunction().method1)
#         bleu_scores.append(bleu)

#     print("\n=== Intent Classification Report ===")
#     print(classification_report(intents_gold, intents_pred))

#     print("\n=== Summary Metrics ===")
#     print(f"Avg Entity Overlap Score: {round(sum(entity_f1_list)/len(entity_f1_list), 4)}")
#     print(f"Avg Tool Call Score:      {round(sum(tool_f1_list)/len(tool_f1_list), 4)}")
#     print(f"Avg BLEU Score:           {round(sum(bleu_scores)/len(bleu_scores), 4)}")


def evaluate(dataset_path: str, mode: str = "lite"):
    """
    Evaluate the LLM predictions in the given dataset file.

    The dataset file should be a JSON file containing a list of objects, where each object has the following properties:

    - predicted: the predicted response from the LLM
    - expected: the gold standard response

    The evaluation is run in one of two modes:

    - lite: computes the following metrics and prints a summary:
        + Intent accuracy: whether the predicted intent matches the gold standard
        + Entity accuracy: how well do the predicted entities match the gold standard?
        + Tool call score: how well do the predicted tool calls match the gold standard?
        + Response similarity: how similar is the predicted response to the gold standard?
        + Confidence score: how confident is the model in its predictions?
    - full: computes the above metrics and also the following metrics and prints a summary:
        + BLEU score: how similar is the predicted response to the gold standard?
        + Tool accuracy: exact match of tool list
        + Internal next steps accuracy: exact match of list

    The results are printed to the console as a table.

    :param dataset_path: the path to the dataset file
    :param mode: the evaluation mode, either 'lite' or 'full'
    """
    with open(dataset_path, "r") as f:
        data = json.load(f)

    if mode == "lite":
        logger.info("Running Lite Evaluation...")
        all_results = []
        for i, ex in enumerate(data):
            metrics = evaluate_lite(ex)
            metrics["llm_score"] = calculate_llm_score(metrics)
            metrics["example_id"] = i
            all_results.append(metrics)

        summary = {
            "num_examples": len(all_results),
            "avg_llm_score": round(sum(r["llm_score"] for r in all_results) / len(all_results), 4),
            "avg_intent_accuracy": round(sum(r["intent_match"] for r in all_results) / len(all_results), 4),
            "avg_entity_accuracy": round(sum(r["entity_accuracy"] for r in all_results) / len(all_results), 4),
            "avg_tool_call_score": round(sum(r["tool_call_score"] for r in all_results) / len(all_results), 4),
            "avg_response_similarity": round(sum(r["response_similarity"] for r in all_results) / len(all_results), 4),
            "avg_confidence_score": round(sum(r["confidence_score"] for r in all_results) / len(all_results), 4),
        }

        logger.info("\n=== Evaluation Summary ===")
        for k, v in summary.items():
            logger.info(f"{k}: {v}")

    elif mode == "full":
        logger.info("Running Full Evaluation...")
        evaluate_full(data)
    else:
        logger.error("Invalid mode. Choose 'lite' or 'full'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True, help="Path to evaluation dataset file")
    parser.add_argument("--mode", type=str, default="lite", choices=["lite", "full"], help="Evaluation mode")

    args = parser.parse_args()
    evaluate(args.file, args.mode)
