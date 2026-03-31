from typing import List, Dict, Any
from tqdm import tqdm
from .base_evaluator import BaseEvaluator
from ..utils.data_utils import save_agent_data

class DialogueEvaluator(BaseEvaluator):
    """
    Evaluator for multi-turn dialogue tasks.
    """
    
    def evaluate(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        dataset format:
        [
            {
                "dialogue_history": [
                    {"role": "user", "content": "..."},
                    {"role": "assistant", "content": "..."},
                    {"role": "user", "content": "..."}
                ],
                "ground_truth": "..."
            }
        ]
        """
        results = []
        
        for idx, item in enumerate(tqdm(dataset, desc="Evaluating Multi-turn Dialogue")):
            history = item.get("dialogue_history", [])
            
            if not history:
                continue
                
            # Copy history to avoid modifying original dataset
            messages = list(history)
            
            # Use model to generate the next response
            response = self.model.generate(messages, max_tokens=1024)
            
            results.append({
                "id": idx,
                "history": history,
                "ground_truth": item.get("ground_truth", ""),
                "ai_answer": response
            })
            
        summary = {
            "total": len(dataset),
            "details": results
        }
        
        save_agent_data(summary, task_name="dialogue_evaluation")
        return summary
