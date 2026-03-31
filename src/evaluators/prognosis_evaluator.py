from typing import List, Dict, Any
from tqdm import tqdm
from .base_evaluator import BaseEvaluator
from ..utils.prompt_utils import load_prompt
from ..utils.data_utils import save_agent_data

class PrognosisEvaluator(BaseEvaluator):
    """
    Evaluator specifically designed for prognosis tasks based on clinical case reports.
    It can generate questions based on clinical info, answer them, and format outputs for the judge.
    """
    
    def generate_questions(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Step 1: Based on raw clinical info (e.g. from prognosis_eval.json),
        use LLM to parse and generate specific prognosis questions.
        """
        prompt_template = load_prompt(f"prognosis_gen_{self.lang}.txt")
        results = []
        
        for idx, item in enumerate(tqdm(dataset, desc="Generating Prognosis Questions")):
            clinical_info = item.get("clinical_info", "")
            
            prompt = prompt_template.format(clinical_info=clinical_info)
            messages = [{"role": "user", "content": prompt}]
            
            # Using service_id=120 equivalent reasoning capability here is recommended
            generated_questions = self.model.generate(messages, max_tokens=1024, temperature=0.7)
            
            new_item = item.copy()
            new_item["generated_questions"] = generated_questions
            results.append(new_item)
            
        save_agent_data(results, task_name="prognosis_question_generation")
        return results

    def evaluate(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Step 2: Answer the prognosis questions based on the clinical info.
        This dataset should ideally have 'clinical_info' and 'questions'.
        """
        prompt_template = load_prompt(f"prognosis_eval_{self.lang}.txt")
        results = []
        
        for idx, item in enumerate(tqdm(dataset, desc="Evaluating Prognosis (Answering)")):
            clinical_info = item.get("clinical_info", "")
            # Support both pre-defined questions or generated questions
            questions = item.get("questions", item.get("generated_questions", ""))
            
            prompt = prompt_template.format(
                clinical_info=clinical_info, 
                questions=questions
            )
            messages = [{"role": "user", "content": prompt}]
            
            ai_answer = self.model.generate(messages, max_tokens=1024, temperature=0.0)
            
            results.append({
                "id": idx,
                "clinical_info": clinical_info,
                "questions": questions,
                "ground_truth": item.get("ground_truth", "N/A"),
                "ai_answer": ai_answer
            })
            
        summary = {
            "total": len(dataset),
            "details": results
        }
        
        save_agent_data(summary, task_name="prognosis_answering")
        return summary
