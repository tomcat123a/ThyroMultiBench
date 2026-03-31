import os

from src.evaluators import MultimodalEvaluator
from src.models import create_model
from src.utils import load_dataset, resolve_script_dir


GEN_PROVIDER = "qwen"
GEN_MODEL_NAME = "qwen-vl-plus"
LANG = "zh"
DATASET_REL_PATH = os.path.join("dataset", "multimodal_tasks", "image_qa.xlsx")


def main() -> None:
    scripts_dir = resolve_script_dir(globals().get("__file__"))
    repo_root = os.path.dirname(scripts_dir)
    dataset_path = os.path.join(repo_root, DATASET_REL_PATH)

    dataset = load_dataset(dataset_path)
    if not dataset:
        print(f"Dataset not found or empty: {dataset_path}")
        return

    gen_model = create_model(provider=GEN_PROVIDER, model_name=GEN_MODEL_NAME)
    evaluator = MultimodalEvaluator(model=gen_model, lang=LANG)
    result = evaluator.evaluate(dataset, task_type="multiple_choice")
    print(f"Accuracy: {result.get('accuracy', 0.0):.2%} ({result.get('correct', 0)}/{result.get('total', 0)})")


if __name__ == "__main__":
    main()

