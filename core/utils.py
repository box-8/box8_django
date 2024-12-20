import os
import json
import shutil
from typing import List, Dict, Any

def get_absolute_path(relative_path: str) -> str:
    parts = relative_path.split('/')
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), *parts)

def save_json(filepath: str, data: Dict[str, Any]) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath: str) -> Dict[str, Any]:
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def delete_directory_recursive(directory: str) -> None:
    if os.path.exists(directory):
        shutil.rmtree(directory)

def list_directory_files(directory: str, extensions: List[str] = None) -> List[str]:
    files = []
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if extensions is None or any(file.endswith(ext) for ext in extensions):
                files.append(file)
    return files
