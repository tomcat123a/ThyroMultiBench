import os
from typing import Optional


def resolve_script_dir(file_value: Optional[str] = None) -> str:
    """
    Resolve a script directory with the following priority:
    1) Use the provided file path (typically __file__) when available.
    2) Fallback to the current working directory.
    """
    if file_value:
        try:
            return os.path.dirname(os.path.abspath(file_value))
        except Exception:
            pass
    return os.getcwd()

