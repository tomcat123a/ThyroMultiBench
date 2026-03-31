import os
import json
from src.models import (
    OpenAIModel, 
    QwenModel, 
    ClaudeModel, 
    GeneralOpenAICompatibleModel
)
from src.evaluators import (
    TextEvaluator, 
    MultimodalEvaluator, 
    JudgeEvaluator,
    PrognosisEvaluator,
    DialogueEvaluator
)
from src.utils import save_agent_data, load_dataset

def evaluate_all():
    """
    Main entry point for batch evaluation of ThyroMultiBench dataset.
    This script demonstrates a complete pipeline: loading datasets from files,
    evaluating text, multimodal, dialogue, and clinical prognosis tasks, 
    and finally using an LLM-as-a-judge to score open-ended responses.
    """
    
    # ---------------------------------------------------------
    # 1. Configuration & Model Initialization
    # ---------------------------------------------------------
    print("Initializing models...")
    
    # ------------------ Generator Model Options ------------------
    # Option 1: Qwen (Aliyun)
    gen_model = QwenModel(model_name="qwen-vl-plus")
    
    # Option 2: Claude (Anthropic)
    # gen_model = ClaudeModel(model_name="claude-3-5-sonnet-20240620")
    
    # Option 3: General OpenAI-compatible API (e.g. vLLM, DeepSeek, Local Models)
    # gen_model = GeneralOpenAICompatibleModel(model_name="your-custom-model")
    
    # ------------------ Judge Model Options ------------------
    # Example: using OpenAI GPT-4o for Judge/Reasoning (service_id=120 equivalent)
    judge_model = OpenAIModel(model_name="gpt-4o")
    
    lang = "en" # Choose "en" or "zh"
    
    # Paths to datasets (assuming user placed them in the dataset folder)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "dataset")
    
    # ---------------------------------------------------------
    # 2. Text Tasks Evaluation (Multiple Choice & Open QA)
    # ---------------------------------------------------------
    print("\n--- Starting Text Task Evaluation ---")
    text_evaluator = TextEvaluator(model=gen_model, lang=lang)
    
    # Load and evaluate Text MCQ
    text_mcq_path = os.path.join(dataset_dir, "text_tasks", "multiple_choice.json")
    text_mcq_data = load_dataset(text_mcq_path)
    if text_mcq_data:
        print(f"Loaded {len(text_mcq_data)} Text MCQ cases.")
        text_mcq_results = text_evaluator.evaluate(text_mcq_data, task_type="multiple_choice")
        print(f"Text MCQ Accuracy: {text_mcq_results.get('accuracy', 0):.2%}")
    else:
        print("Skipping Text MCQ evaluation (Dataset not found).")
        text_mcq_results = {}
        
    # Load and evaluate Text Open QA
    text_qa_path = os.path.join(dataset_dir, "text_tasks", "open_qa.json")
    text_qa_data = load_dataset(text_qa_path)
    if text_qa_data:
        print(f"Loaded {len(text_qa_data)} Text Open QA cases.")
        text_qa_results = text_evaluator.evaluate(text_qa_data, task_type="open_qa")
    else:
        print("Skipping Text Open QA evaluation (Dataset not found).")
        text_qa_results = {}
        
    # ---------------------------------------------------------
    # 3. Multimodal Tasks Evaluation (Image + Text)
    # ---------------------------------------------------------
    print("\n--- Starting Multimodal Task Evaluation ---")
    multimodal_evaluator = MultimodalEvaluator(model=gen_model, lang=lang)
    
    mm_mcq_path = os.path.join(dataset_dir, "multimodal_tasks", "image_qa.xlsx")
    mm_mcq_data = load_dataset(mm_mcq_path)
    if mm_mcq_data:
        print(f"Loaded {len(mm_mcq_data)} Multimodal MCQ cases from Excel.")
        # Uncomment below to actually run if you have valid image URLs
        # mm_mcq_results = multimodal_evaluator.evaluate(mm_mcq_data, task_type="multiple_choice")
        # print(f"Multimodal MCQ Accuracy: {mm_mcq_results.get('accuracy', 0):.2%}")
        print("Multimodal evaluation logic ready. Ensure valid image URLs/paths before uncommenting.")
    else:
        print("Skipping Multimodal evaluation (Dataset not found).")

    # ---------------------------------------------------------
    # 4. Clinical Prognosis Task (Reasoning & Question Generation)
    # ---------------------------------------------------------
    print("\n--- Starting Clinical Prognosis Evaluation ---")
    prognosis_evaluator = PrognosisEvaluator(model=judge_model, lang=lang) # Use reasoning model
    
    prognosis_path = os.path.join(dataset_dir, "prognosis", "prognosis_eval.json")
    prognosis_data = load_dataset(prognosis_path)
    
    if prognosis_data:
        print(f"Loaded {len(prognosis_data)} Clinical Prognosis cases.")
        print("Step 4.1: Generating prognosis questions from clinical info...")
        prognosis_with_qs = prognosis_evaluator.generate_questions(prognosis_data)
        
        print("Step 4.2: Answering the generated prognosis questions...")
        prognosis_results = prognosis_evaluator.evaluate(prognosis_with_qs)
    else:
        print("Skipping Clinical Prognosis evaluation (Dataset not found).")
        prognosis_results = {}
        
    # ---------------------------------------------------------
    # 5. Multi-turn Dialogue Evaluation
    # ---------------------------------------------------------
    print("\n--- Starting Multi-turn Dialogue Evaluation ---")
    dialogue_evaluator = DialogueEvaluator(model=gen_model, lang=lang)
    
    dialogue_path = os.path.join(dataset_dir, "text_tasks", "dialogue.json")
    dialogue_data = load_dataset(dialogue_path)
    if dialogue_data:
        print(f"Loaded {len(dialogue_data)} Dialogue cases.")
        dialogue_results = dialogue_evaluator.evaluate(dialogue_data)
    else:
        print("Skipping Dialogue evaluation (Dataset not found).")
        dialogue_results = {}

    # ---------------------------------------------------------
    # 6. LLM as a Judge Evaluation (For Open QA & Prognosis)
    # ---------------------------------------------------------
    print("\n--- Starting LLM-as-a-Judge Evaluation ---")
    judge = JudgeEvaluator(judge_model=judge_model, lang=lang)
    
    # 6.1 Judge Open QA
    if text_qa_results.get("details"):
        print("Judging Open QA results...")
        judge_data_qa = [
            {
                "question": item.get("question"),
                "ground_truth": item.get("ground_truth"),
                "ai_answer": item.get("ai_answer")
            } for item in text_qa_results["details"]
        ]
        qa_judge_results = judge.evaluate(judge_data_qa)
        print(f"Open QA Judge Average Score: {qa_judge_results.get('average_score', 0):.2f}/10")
    else:
        qa_judge_results = {}
        
    # 6.2 Judge Prognosis
    if prognosis_results.get("details"):
        print("Judging Prognosis results...")
        judge_data_prog = [
            {
                "question": item.get("questions"), # The generated questions
                "ground_truth": item.get("ground_truth"),
                "ai_answer": item.get("ai_answer")
            } for item in prognosis_results["details"]
        ]
        prog_judge_results = judge.evaluate(judge_data_prog)
        print(f"Prognosis Judge Average Score: {prog_judge_results.get('average_score', 0):.2f}/10")
    else:
        prog_judge_results = {}

    # ---------------------------------------------------------
    # 7. Final Report
    # ---------------------------------------------------------
    print("\n=== Final Evaluation Report ===")
    report = {
        "text_mcq_accuracy": text_mcq_results.get("accuracy"),
        "text_open_qa_judge_score": qa_judge_results.get("average_score"),
        "prognosis_judge_score": prog_judge_results.get("average_score")
    }
    
    report_path = save_agent_data(report, task_name="final_evaluation_report")
    print(f"Evaluation completed. Final report saved to: {report_path}")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    evaluate_all()
