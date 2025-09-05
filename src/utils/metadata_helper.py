import json
from pathlib import Path


def update_metadata(file_path: str, key: str, value: str) -> None:
    path = Path(file_path)
    
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}

    data[key] = value
    path.write_text(json.dumps(data, ensure_ascii=False, indent=4), encoding="utf-8")
    print(f"✅ Updated {file_path} with '{key}: {value}'.")


def print_metadata(file_path: str) -> None:
    path = Path(file_path)

    if not path.exists():
        print(f"⚠️ File {file_path} does not exist.")
        return

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        print(json.dumps(data, ensure_ascii=False, indent=4))
    except json.JSONDecodeError:
        print(f"⚠️ File {file_path} is not valid JSON.")
