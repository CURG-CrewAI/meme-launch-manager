def validate_choice(choice: int | None, max_len: int, default: int = 1) -> int:
    if choice is None:
        return default
    if 1 <= choice <= max_len:
        return choice
    return default


def pick_trend(trends: list[dict], idx: int) -> dict | None:
    if not trends:
        return None
    if 1 <= idx <= len(trends):
        return trends[idx - 1]
    return trends[0]
