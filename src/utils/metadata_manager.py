import json
from pathlib import Path


def add_metadata(file_path: str, key: str, value: str) -> None:
    """
    Args:
        file_path (str): JSON 파일 경로
        key (str): 추가할 키
        value (str): 추가할 값
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
    metadata.json 파일 내용을 터미널에 출력합니다.
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
