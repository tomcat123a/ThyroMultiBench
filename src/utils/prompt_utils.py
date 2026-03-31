import os
from .config_utils import get_script_dir

def load_prompt(prompt_filename: str) -> str:
    """
    Load a prompt template from the `prompt` directory.
    Follows user rule: always load from `prompt` directory, saving templates as txt.
    """
    script_dir = get_script_dir()
    project_root = os.path.dirname(os.path.dirname(script_dir))
    prompt_path = os.path.join(project_root, "prompt", prompt_filename)
    
    if not os.path.exists(prompt_path):
        print(f"Warning: Prompt file not found at {prompt_path}")
        return ""
        
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()
