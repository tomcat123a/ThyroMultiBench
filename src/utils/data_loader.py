import json
import os
import pandas as pd
from typing import List, Dict, Any

def load_json_dataset(file_path: str) -> List[Dict[str, Any]]:
    """
    Load a JSON or JSONL dataset.
    Returns a list of dictionaries.
    """
    if not os.path.exists(file_path):
        print(f"Warning: Dataset file not found at {file_path}")
        return []
        
    data = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if file_path.endswith(".jsonl"):
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            else:
                data = json.load(f)
                if isinstance(data, dict):
                    # If it's a single dict, wrap in list or extract the main array
                    data = [data]
    except Exception as e:
        print(f"Error loading JSON dataset {file_path}: {e}")
        
    return data

def load_excel_dataset(file_path: str) -> List[Dict[str, Any]]:
    """
    Load an Excel (.xlsx) dataset using pandas.
    Returns a list of dictionaries.
    """
    if not os.path.exists(file_path):
        print(f"Warning: Dataset file not found at {file_path}")
        return []
        
    try:
        df = pd.read_excel(file_path)
        # Replace NaN with empty string or None for JSON serialization safety
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error loading Excel dataset {file_path}: {e}")
        return []

def load_dataset(file_path: str) -> List[Dict[str, Any]]:
    """
    Generic dataset loader determining format by extension.
    """
    if file_path.endswith(".xlsx") or file_path.endswith(".xls"):
        return load_excel_dataset(file_path)
    elif file_path.endswith(".json") or file_path.endswith(".jsonl"):
        return load_json_dataset(file_path)
    else:
        print(f"Unsupported file format for {file_path}")
        return []
