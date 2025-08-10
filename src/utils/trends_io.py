from __future__ import annotations
from pathlib import Path
import json, ast
from typing import Any


def load_trends_from_file(path: str | Path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def parse_raw_trends(raw: Any) -> list[dict]:
    if not raw:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            pass
        try:
            data = ast.literal_eval(raw)
            return data if isinstance(data, list) else []
        except (ValueError, SyntaxError):
            return []
    return []
