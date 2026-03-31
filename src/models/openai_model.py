import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .base_model import BaseModel
from ..utils.config_utils import load_config

class OpenAIModel(BaseModel):
    """
    OpenAI model wrapper for text and multimodal tasks.
    Supports gpt-4, gpt-4-turbo, gpt-3.5-turbo, gpt-4o, etc.
    """
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key, **kwargs)
        
        # Load config if API key is not provided directly
        if not self.api_key:
            config = load_config()
            self.api_key = config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
            
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, messages: List[Dict[str, Any]], max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """
        Generate response from OpenAI API.
        Does NOT use streaming based on user instructions.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return ""
