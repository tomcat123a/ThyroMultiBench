import os
import json
from typing import List, Dict, Any, Optional
from .base_model import BaseModel
from ..utils.config_utils import load_config

# Import dashscope if available
try:
    import dashscope
    from dashscope import MultiModalConversation, Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False

class QwenModel(BaseModel):
    """
    Qwen model wrapper for text and multimodal tasks (via Aliyun DashScope).
    """
    def __init__(self, model_name: str = "qwen-vl-plus", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, api_key, **kwargs)
        
        if not DASHSCOPE_AVAILABLE:
            raise ImportError("dashscope module is not installed. Please install it using `pip install dashscope`.")
            
        # Load config if API key is not provided directly
        if not self.api_key:
            config = load_config()
            self.api_key = config.get("dashscope_api_key") or os.getenv("DASHSCOPE_API_KEY")
            
        dashscope.api_key = self.api_key

    def generate(self, messages: List[Dict[str, Any]], max_tokens: int = 1024, temperature: float = 0.0) -> str:
        """
        Generate response from Qwen API.
        Does NOT use streaming based on user instructions.
        """
        is_multimodal = any(
            isinstance(msg.get("content"), list) for msg in messages
        )

        try:
            if is_multimodal:
                response = MultiModalConversation.call(
                    model=self.model_name,
                    messages=messages,
                    max_length=max_tokens,
                    top_p=0.8,
                    stream=False
                )
                if response.status_code == 200:
                    return response.output.choices[0].message.content[0].get('text', '')
                else:
                    print(f"Error in DashScope Multimodal API: {response.code} - {response.message}")
                    return ""
            else:
                response = Generation.call(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    result_format='message',
                    stream=False
                )
                if response.status_code == 200:
                    return response.output.choices[0].message.content
                else:
                    print(f"Error in DashScope Generation API: {response.code} - {response.message}")
                    return ""
        except Exception as e:
            print(f"Exception calling Qwen API: {e}")
            return ""
