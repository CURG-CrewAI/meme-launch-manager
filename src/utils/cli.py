import unicodedata


def format_trends(trends: list[dict]) -> str:
    lines = ["\n📢 Top trending keywords with reasons:\n"]
    for idx, item in enumerate(trends, start=1):
        keyword = item.get("keyword", "N/A")
        reason = item.get("why_trending", "No explanation available.")
        lines.append(f"{idx}. {keyword} — {reason}")
    return "\n".join(lines)


def prompt_choice(prompt: str, default: int = 1) -> str:
    choice_str = input(f"\n{prompt} (default={default}): ").strip()
    print(f"[DEBUG] Raw input: {repr(choice_str)}")
    return choice_str


def normalize_numeric(choice_str: str) -> int | None:
    digits = "".join(
        ch for ch in choice_str if unicodedata.category(ch).startswith("N")
    )
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None
