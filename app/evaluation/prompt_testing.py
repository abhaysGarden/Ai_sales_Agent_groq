import json
from pathlib import Path
from typing import Dict, Callable
from evaluation import evaluate_lite, calculate_llm_score
from app.llm.prompts import orchestration_prompt_v1 as run_prompt
from app.evaluation.golden_dataset import GOLDEN_DATASET
from app.evaluation.metrics import compute_intent_f1, compute_entity_overlap, similarity_score
from app.evaluation.score import compute_llm_score

def run_prompt_variant(prompt_fn: Callable, name: str) -> Dict:
    """
    Evaluates a prompt function against a golden dataset and computes average scores.

    Args:
        prompt_fn (Callable): A function that generates a response based on conversation history,
                              the current message, and prospect ID.
        name (str): The name of the prompt variant being evaluated.

    Returns:
        Dict: A dictionary containing the prompt name and the average scores for intent F1, 
              entity F1, response similarity, confidence score, tool call score, and LLM score.
    """

    results = []
    for example in GOLDEN_DATASET:
        output = prompt_fn(
            conversation_history=example["conversation_history"],
            current_message=example["current_prospect_message"],
            prospect_id=example["prospect_id"]
        )

        truth = example["ground_truth"]
        scores = {
            "intent_f1": compute_intent_f1(output["intent"], truth["intent"]),
            "entity_f1": compute_entity_overlap(output["entities"], truth["entities"])["f1"],
            "response_similarity": similarity_score(
                output["suggested_response_draft"], truth["suggested_response_draft"]
            ),
            "confidence_score": output.get("confidence_score", 0.0),
            "tool_call_score": 1.0 if "tools_to_call" not in truth or "tools_to_call" not in output else 0.8  # Simplified
            
        }

        scores["llm_score"] = compute_llm_score(scores)
        results.append(scores)

    avg_scores = {
        k: round(sum(r[k] for r in results) / len(results), 4)
        for k in results[0]
    }

    return {"prompt_name": name, "scores": avg_scores}


def load_prompt_versions(prompt_dir: str) -> Dict[str, str]:
    """
    Loads all prompt versions from a directory containing text files. Each file
    is expected to contain a single prompt template, and the file name is used
    as the prompt version name.

    Args:
        prompt_dir (str): The directory containing the prompt files.

    Returns:
        Dict[str, str]: A dictionary mapping prompt version names to their
        corresponding prompt templates.
    """
    prompts = {}
    for path in Path(prompt_dir).glob("*.txt"):
        with open(path) as f:
            prompts[path.stem] = f.read()
    return prompts


def run_prompt_on_example(prompt_template: str, example: Dict) -> Dict:
    # Combine history + current message into a single prompt input
    """
    Generates a prediction using a given prompt template and example data.

    Args:
        prompt_template (str): The template for the prompt to be used with the LLM.
        example (Dict): A dictionary containing the conversation history, current prospect message,
                        and ground truth data.

    Returns:
        Dict: A dictionary containing the predicted response and the expected ground truth.
    """

    conversation = "\n".join([f"{msg['sender']}: {msg['content']}" for msg in example["conversation_history"]])
    input_text = f"{conversation}\nprospect: {example['current_prospect_message']}"
    
    # Call LLM with specific prompt
    response = run_prompt(prompt_template, input_text)

    return {
        "predicted": response,
        "expected": example["ground_truth"]
    }


def test_all_prompts(golden_path: str, prompt_dir: str):
    """
    Tests multiple prompt versions against a golden dataset and evaluates their performance.

    This function loads a set of prompt templates from a directory, applies each template to 
    each example in a provided golden dataset, and evaluates the output using various metrics. 
    The results, including average LLM scores and detailed metrics for each example, are printed 
    and returned.

    Args:
        golden_path (str): The file path to the golden dataset in JSON format.
        prompt_dir (str): The directory containing the prompt files.

    Returns:
        Dict[str, Dict]: A dictionary mapping each prompt version name to its average LLM score 
        and details of metrics for each example.
    """

    with open(golden_path, "r") as f:
        golden_dataset = json.load(f)

    prompt_versions = load_prompt_versions(prompt_dir)

    results = {}

    for version_name, prompt_template in prompt_versions.items():
        print(f"\n Testing prompt version: {version_name}")
        version_results = []

        for example in golden_dataset:
            try:
                full_example = run_prompt_on_example(prompt_template, example)
                metrics = evaluate_lite(full_example)
                metrics["llm_score"] = calculate_llm_score(metrics)
                version_results.append(metrics)
            except Exception as e:
                print(f"Error on example {example['id']}: {e}")

        avg_score = round(sum(m["llm_score"] for m in version_results) / len(version_results), 4)
        results[version_name] = {
            "avg_llm_score": avg_score,
            "details": version_results
        }

    print("\n=== Prompt Version Comparison ===")
    for v, r in results.items():
        print(f"{v}: LLM Score = {r['avg_llm_score']}")

    return results


if __name__ == "__main__":
    test_all_prompts(
        golden_path="evaluation/golden_dataset.json",
        prompt_dir="prompts/"
    )
