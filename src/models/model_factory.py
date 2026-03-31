from typing import Any, Dict, Optional

from .base_model import BaseModel
from .openai_model import OpenAIModel
from .qwen_model import QwenModel
from .claude_model import ClaudeModel
from .general_model import GeneralOpenAICompatibleModel


def create_model(
    provider: str,
    model_name: str,
    extra: Optional[Dict[str, Any]] = None,
) -> BaseModel:
    provider_norm = (provider or "").strip().lower()
    extra = extra or {}

    if provider_norm in {"openai", "gpt"}:
        return OpenAIModel(model_name=model_name, **extra)
    if provider_norm in {"qwen", "dashscope", "aliyun"}:
        return QwenModel(model_name=model_name, **extra)
    if provider_norm in {"claude", "anthropic"}:
        return ClaudeModel(model_name=model_name, **extra)
    if provider_norm in {"general", "openai_compatible", "openai-compatible"}:
        return GeneralOpenAICompatibleModel(model_name=model_name, **extra)

    raise ValueError(f"Unknown provider: {provider}")

