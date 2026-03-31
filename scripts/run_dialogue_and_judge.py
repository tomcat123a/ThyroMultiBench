import json
import os

from src.evaluators import DialogueEvaluator, JudgeEvaluator
from src.models import create_model
from src.utils import load_dataset, resolve_script_dir


GEN_PROVIDER = "qwen"
GEN_MODEL_NAME = "qwen-plus"
JUDGE_PROVIDER = "openai"
JUDGE_MODEL_NAME = "gpt-4o"
LANG = "zh"
DATASET_REL_PATH = os.path.join("dataset", "text_tasks", "dialogue.json")
RUN_JUDGE = True


def _format_history_as_question(history) -> str:
    try:
        return json.dumps(history, ensure_ascii=False)
    except Exception:
        return str(history)


def main() -> None:
    scripts_dir = resolve_script_dir(globals().get("__file__"))
    repo_root = os.path.dirname(scripts_dir)
    dataset_path = os.path.join(repo_root, DATASET_REL_PATH)

    dataset = load_dataset(dataset_path)
    if not dataset:
        print(f"Dataset not found or empty: {dataset_path}")
        return

    gen_model = create_model(provider=GEN_PROVIDER, model_name=GEN_MODEL_NAME)
    dialogue_evaluator = DialogueEvaluator(model=gen_model, lang=LANG)
    gen_result = dialogue_evaluator.evaluate(dataset)
    print(f"Generated: {gen_result.get('total', 0)} cases")

    if not RUN_JUDGE:
        return

    judge_input = []
    for item in gen_result.get("details", []):
        judge_input.append(
            {
                "question": _format_history_as_question(item.get("history", [])),
                "ground_truth": item.get("ground_truth", ""),
                "ai_answer": item.get("ai_answer", ""),
            }
        )

    judge_model = create_model(provider=JUDGE_PROVIDER, model_name=JUDGE_MODEL_NAME)
    judge_evaluator = JudgeEvaluator(judge_model=judge_model, lang=LANG)
    judge_result = judge_evaluator.evaluate(judge_input)
    print(f"Average score: {judge_result.get('average_score', 0.0):.2f} (valid={judge_result.get('valid_cases', 0)})")


if __name__ == "__main__":
    main()

