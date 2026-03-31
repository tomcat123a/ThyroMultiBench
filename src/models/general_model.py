import os
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .base_model import BaseModel
from ..utils.config_utils import load_config

class GeneralOpenAICompatibleModel(BaseModel):
    """
    A general model wrapper that uses the OpenAI SDK to connect to any OpenAI-compatible API endpoints.
    Useful for local models (vLLM, Ollama, LM Studio) or third-party APIs (DeepSeek, Moonshot, etc.)
    """
    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key, **kwargs)
        
        config = load_config()
        
        # Load API key
        if not self.api_key:
            self.api_key = config.get("general_api_key") or os.getenv("GENERAL_API_KEY", "dummy_key")
            
        # Load Base URL
        self.base_url = base_url or config.get("general_api_base") or os.getenv("GENERAL_API_BASE")
        
        if not self.base_url:
            print("Warning: No base_url provided for GeneralOpenAICompatibleModel. Ensure it's set in config.json as 'general_api_base'.")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def generate(self, messages: List[Dict[str, Any]], max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """
        Generate response using OpenAI SDK connected to a custom endpoint.
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
            print(f"Error calling General API ({self.base_url}): {e}")
            return ""
