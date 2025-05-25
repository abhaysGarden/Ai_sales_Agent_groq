# app/evaluation/runner.py

from app.evaluation.prompt_testing import run_prompt_variant
from app.llm.prompts import orchestration_prompt_v1, orchestration_prompt_v2

def run_all():
    """
    Run all evaluation prompts and print out the results.

    This function will run evaluation prompts (currently just v1_default and v2_chain_of_thought),
    and print out their results in a pretty format. The results include the score for each subtask
    (intent recognition, entity recognition, suggested response, etc.) as well as the overall score.

    The results are printed to stdout, but could be modified to write to a file or return the results
    instead.

    Example output:

        Prompt: v1_default
          intent_f1: 0.80
          entity_f1: 0.85
          response_similarity: 0.92
          confidence_score: 0.85
          tool_call_score: 0.90
          llm_score: 0.87
        --------------------
        Prompt: v2_chain_of_thought
          intent_f1: 0.95
          entity_f1: 0.98
          response_similarity: 0.96
          confidence_score: 0.92
          tool_call_score: 0.95
          llm_score: 0.94
        --------------------
    """
    results = []
    results.append(run_prompt_variant(orchestration_prompt_v1, "v1_default"))
    results.append(run_prompt_variant(orchestration_prompt_v2, "v2_chain_of_thought"))

    for r in results:
        print(f"Prompt: {r['prompt_name']}")
        for k, v in r["scores"].items():
            print(f"  {k}: {v:.2f}")
        print("-" * 20)

if __name__ == "__main__":
    run_all()
