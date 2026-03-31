import os
import json
from datetime import datetime
from typing import Any, Dict
import uuid
from .config_utils import get_script_dir

def save_agent_data(data: Any, task_name: str = "task") -> str:
    """
    Save agent data (e.g. LLM generated results) to agent_data directory.
    Follows user rule: save as txt in agent_data/<uuid_based_on_task>/ directory.
    """
    script_dir = get_script_dir()
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    task_id = str(uuid.uuid4())
    agent_data_dir = os.path.join(project_root, "agent_data", f"{task_name}_{task_id}")
    
    os.makedirs(agent_data_dir, exist_ok=True)
    
    file_path = os.path.join(agent_data_dir, "result.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        if isinstance(data, dict) or isinstance(data, list):
            json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            f.write(str(data))
            
    return file_path
