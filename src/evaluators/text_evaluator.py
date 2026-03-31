from typing import List, Dict, Any
from tqdm import tqdm
from .base_evaluator import BaseEvaluator
from ..utils.prompt_utils import load_prompt
from ..utils.data_utils import save_agent_data
from ..utils.mcq_utils import extract_option_letters_from_options_text, parse_mcq_prediction

class TextEvaluator(BaseEvaluator):
    """
    Evaluator for pure text tasks, including multiple choice and open QA.
    """
    
    def evaluate_multiple_choice(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate multiple choice questions. Calculates accuracy.
        """
        prompt_template = load_prompt(f"multiple_choice_{self.lang}.txt")
        
        correct_count = 0
        results = []
        
        for idx, item in enumerate(tqdm(dataset, desc="Evaluating Text Multiple Choice")):
            question = item.get("question", "")
            options = item.get("options", "")
            ground_truth = item.get("answer", "").strip().upper()
            
            prompt = prompt_template.format(question=question, options=options)
            messages = [{"role": "user", "content": prompt}]
            
            response = self.model.generate(messages, max_tokens=1024)
            
            valid_letters = extract_option_letters_from_options_text(options)
            predicted = parse_mcq_prediction(response, valid_options=valid_letters)
            
            is_correct = (predicted == ground_truth)
            if is_correct:
                correct_count += 1
                
            results.append({
                "id": idx,
                "question": question,
                "predicted": predicted,
                "ground_truth": ground_truth,
                "is_correct": is_correct,
                "raw_response": response
            })
            
        accuracy = correct_count / len(dataset) if dataset else 0.0
        
        summary = {
            "accuracy": accuracy,
            "total": len(dataset),
            "correct": correct_count,
            "details": results
        }
        
        save_agent_data(summary, task_name="text_mcq_evaluation")
        return summary
        
    def evaluate_open_qa(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate Open QA. Just generates answers, then typically relies on JudgeEvaluator to score.
        """
        prompt_template = load_prompt(f"open_qa_{self.lang}.txt")
        
        results = []
        
        for idx, item in enumerate(tqdm(dataset, desc="Evaluating Open QA")):
            question = item.get("question", "")
            
            prompt = prompt_template.format(question=question)
            messages = [{"role": "user", "content": prompt}]
            
            response = self.model.generate(messages, max_tokens=1024)
            
            results.append({
                "id": idx,
                "question": question,
                "ground_truth": item.get("answer", ""),
                "ai_answer": response
            })
            
        summary = {
            "total": len(dataset),
            "details": results
        }
        
        save_agent_data(summary, task_name="text_open_qa_generation")
        return summary
        
    def evaluate(self, dataset: List[Dict[str, Any]], task_type: str = "multiple_choice") -> Dict[str, Any]:
        if task_type == "multiple_choice":
            return self.evaluate_multiple_choice(dataset)
        elif task_type == "open_qa":
            return self.evaluate_open_qa(dataset)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
