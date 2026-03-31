import os

from src.evaluators import JudgeEvaluator, PrognosisEvaluator
from src.models import create_model
from src.utils import load_dataset, resolve_script_dir


QUESTION_PROVIDER = "openai"
QUESTION_MODEL_NAME = "gpt-4o"
ANSWER_PROVIDER = "qwen"
ANSWER_MODEL_NAME = "qwen-plus"
JUDGE_PROVIDER = "openai"
JUDGE_MODEL_NAME = "gpt-4o"
LANG = "zh"
DATASET_REL_PATH = os.path.join("dataset", "prognosis", "prognosis_eval.json")
RUN_JUDGE = True


def main() -> None:
    scripts_dir = resolve_script_dir(globals().get("__file__"))
    repo_root = os.path.dirname(scripts_dir)
    dataset_path = os.path.join(repo_root, DATASET_REL_PATH)

    dataset = load_dataset(dataset_path)
    if not dataset:
        print(f"Dataset not found or empty: {dataset_path}")
        return

    question_model = create_model(provider=QUESTION_PROVIDER, model_name=QUESTION_MODEL_NAME)
    prognosis_question_evaluator = PrognosisEvaluator(model=question_model, lang=LANG)
    with_questions = prognosis_question_evaluator.generate_questions(dataset)

    answer_model = create_model(provider=ANSWER_PROVIDER, model_name=ANSWER_MODEL_NAME)
    prognosis_answer_evaluator = PrognosisEvaluator(model=answer_model, lang=LANG)
    gen_result = prognosis_answer_evaluator.evaluate(with_questions)
    print(f"Generated: {gen_result.get('total', 0)} cases")

    if not RUN_JUDGE:
        return

    judge_input = []
    for item in gen_result.get("details", []):
        question = f"{item.get('clinical_info', '')}\n\n{item.get('questions', '')}"
        judge_input.append(
            {
                "question": question,
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

