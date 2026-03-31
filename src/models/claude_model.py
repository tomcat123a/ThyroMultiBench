import os
from typing import List, Dict, Any, Optional
from .base_model import BaseModel
from ..utils.config_utils import load_config

# Import anthropic if available
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

class ClaudeModel(BaseModel):
    """
    Claude model wrapper for text and multimodal tasks using the official Anthropic API.
    Supports claude-3-5-sonnet, claude-3-opus, etc.
    """
    def __init__(self, model_name: str = "claude-3-5-sonnet-20240620", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key, **kwargs)
        
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic module is not installed. Please install it using `pip install anthropic`.")
            
        # Load config if API key is not provided directly
        if not self.api_key:
            config = load_config()
            self.api_key = config.get("anthropic_api_key") or os.getenv("ANTHROPIC_API_KEY")
            
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def _convert_messages_format(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert standard OpenAI-like messages format to Anthropic format if needed.
        Particularly handles multimodal image blocks.
        """
        anthropic_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # If content is string, keep it simple
            if isinstance(content, str):
                anthropic_messages.append({"role": role, "content": content})
            elif isinstance(content, list):
                # Handle multimodal blocks
                new_content = []
                for block in content:
                    if "text" in block:
                        new_content.append({"type": "text", "text": block["text"]})
                    elif "image" in block:
                        # Assumes image is base64 for Claude
                        # In real scenario, need to fetch URL to base64 if it's a URL
                        new_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg", # Defaulting to jpeg, should be dynamic in production
                                "data": block["image"]
                            }
                        })
                anthropic_messages.append({"role": role, "content": new_content})
                
        return anthropic_messages

    def generate(self, messages: List[Dict[str, Any]], max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """
        Generate response from Anthropic API.
        """
        try:
            formatted_messages = self._convert_messages_format(messages)
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=formatted_messages
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return ""
