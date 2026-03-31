import json
from typing import List, Dict, Any
from tqdm import tqdm
from .base_evaluator import BaseEvaluator
from ..utils.prompt_utils import load_prompt
from ..utils.data_utils import save_agent_data
from ..models.base_model import BaseModel

class JudgeEvaluator(BaseEvaluator):
    """
    LLM-as-a-judge Evaluator.
    Uses the judge model to score open QA and multi-turn dialogue based on ground truth.
    """
    
    def __init__(self, judge_model: BaseModel, lang: str = "en"):
        super().__init__(judge_model, lang)
        self.prompt_template = load_prompt(f"judge_{self.lang}.txt")
        
    def evaluate(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        dataset format:
        [
            {"question": "...", "ground_truth": "...", "ai_answer": "..."}
        ]
        """
        results = []
        total_score = 0
        valid_cases = 0
        
        for idx, item in enumerate(tqdm(dataset, desc="Judge Evaluating")):
            question = item.get("question", "")
            ground_truth = item.get("ground_truth", "")
            ai_answer = item.get("ai_answer", "")
            
            prompt = self.prompt_template.format(
                question=question,
                ground_truth=ground_truth,
                ai_answer=ai_answer
            )
            
            messages = [{"role": "user", "content": prompt}]
            response = self.model.generate(messages, max_tokens=256, temperature=0.0)
            
            try:
                # Clean up response to get pure JSON if wrapped in markdown
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:-3].strip()
                
                eval_result = json.loads(clean_response)
                score = int(eval_result.get("score", 0))
                reason = eval_result.get("reason", "")
                
                results.append({
                    "id": idx,
                    "question": question,
                    "score": score,
                    "reason": reason
                })
                
                total_score += score
                valid_cases += 1
                
            except Exception as e:
                print(f"Error parsing judge response for item {idx}: {e}")
                results.append({
                    "id": idx,
                    "error": str(e),
                    "raw_response": response
                })
                
        avg_score = total_score / valid_cases if valid_cases > 0 else 0.0
        
        summary = {
            "average_score": avg_score,
            "total_cases": len(dataset),
            "valid_cases": valid_cases,
            "details": results
        }
        
        # Save detailed results to agent_data as per user rule
        save_agent_data(summary, task_name="judge_evaluation")
        
        return summary
