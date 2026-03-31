from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class BaseModel(ABC):
    """
    Base class for Large Language Models.
    Provides a unified interface for text and multimodal generation.
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        self.model_name = model_name
        self.api_key = api_key
        self.kwargs = kwargs
        
    @abstractmethod
    def generate(self, messages: List[Dict[str, Any]], max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """
        Generate a response given a list of messages.
        
        Args:
            messages: A list of message dictionaries (e.g., {"role": "user", "content": "..."}).
                      For multimodal, content can be a list containing text and image URLs/base64.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            
        Returns:
            The generated text string.
        """
        pass
