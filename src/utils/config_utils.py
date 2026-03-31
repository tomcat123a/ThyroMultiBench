import os
import json
from pathlib import Path
from typing import Dict, Any
from .path_utils import resolve_script_dir

def get_script_dir() -> str:
    """
    Get the script directory. Resolves using __file__ if possible,
    otherwise falls back to os.getcwd().
    """
    return resolve_script_dir(globals().get("__file__"))

def load_config() -> Dict[str, Any]:
    """
    Load configuration following the priority:
    1. Current working directory (CWD/config.json)
    2. Project root directory (config.json)
    """
    cwd = os.getcwd()
    cwd_config = os.path.join(cwd, "config.json")
    
    if os.path.exists(cwd_config):
        with open(cwd_config, "r", encoding="utf-8") as f:
            return json.load(f)
            
    # Fallback to finding project root (assuming this file is in src/utils)
    script_dir = get_script_dir()
    project_root = os.path.dirname(os.path.dirname(script_dir))
    root_config = os.path.join(project_root, "config.json")
    
    if os.path.exists(root_config):
        with open(root_config, "r", encoding="utf-8") as f:
            return json.load(f)
            
    return {}
