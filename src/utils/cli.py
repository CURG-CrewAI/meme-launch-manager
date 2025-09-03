# ==========Print==========


def print_trends(trends: list[dict]):
    print("\n\n📢 Top trending keywords with reasons:\n")
    for idx, item in enumerate(trends, start=1):
        keyword = item.get("keyword", "N/A")
        reason = item.get("why_trending", "No explanation available.")
        print(f"{idx}. {keyword} — {reason}")


# ==========Prompt==========


def prompt_choice_trend(trends: list[dict], default: int = 1) -> dict | None:
    choiced = input(
        f"\nChoose the trend keyword number you want (default={default}): "
    ).strip()

    if not choiced.isdigit():
        print(f"⚠️ Invalid input (not a number). Default ({default}) selected.")
        selected_number = default
    else:
        number = int(choiced)
        if 1 <= number <= len(trends):
            selected_number = number
        else:
            print(f"⚠️ Invalid range. Default ({default}) selected.")
            selected_number = default

    selected_trend = trends[selected_number - 1]
    print(f"\n✅ Selected keyword: {selected_trend.get('keyword', 'N/A')}")
    return selected_trend


def prompt_make_site(prompt: str, default: str = "n") -> bool:
    raw = input(f"\n{prompt} (default={default}): ").strip()
    print(f"[DEBUG] Raw input: {repr(raw)}")
    return raw.lower() in ("y", "yes")
