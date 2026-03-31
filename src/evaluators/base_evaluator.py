from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models.base_model import BaseModel

class BaseEvaluator(ABC):
    """
    Base Evaluator class. All evaluators must inherit from this class.
    """
    
    def __init__(self, model: BaseModel, lang: str = "en"):
        self.model = model
        self.lang = lang
        
    @abstractmethod
    def evaluate(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate the model on a given dataset.
        
        Args:
            dataset: A list of dicts representing the test cases.
            
        Returns:
            A dictionary containing the evaluation metrics (e.g. accuracy).
        """
        pass
