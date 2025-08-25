import json
from pathlib import Path


def add_metadata(file_path: str, key: str, value: str) -> None:
    """
    Args:
        file_path (str): JSON file path
        key (str): key to add
        value (str): value to add
    """

    path = Path(file_path)

    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    data[key] = value

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ {file_path}에 '{key}: {value}' 추가 완료.")


def print_metadata(file_path: str) -> None:
    """
    Print metadata.json
    """
    path = Path(file_path)

    if not path.exists():
        print(f"⚠️ {file_path} 파일이 존재하지 않습니다.")
        return

    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            print(json.dumps(data, ensure_ascii=False, indent=4))
        except json.JSONDecodeError:
            print(f"⚠️ {file_path} 파일이 올바른 JSON 형식이 아닙니다.")
