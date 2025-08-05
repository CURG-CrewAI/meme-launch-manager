import re

def parse_markdown_inline(text: str) -> list:
    """
    Markdown 인라인 스타일을 Notion rich_text 형식으로 변환
    지원: **bold**, *italic*, __bold__, _italic_, ***bold+italic***
    """
    patterns = [
        (r"\*\*\*(.+?)\*\*\*", {"bold": True, "italic": True}),
        (r"\*\*(.+?)\*\*", {"bold": True}),
        (r"\*(.+?)\*", {"italic": True}),
        (r"__(.+?)__", {"bold": True}),
        (r"_(.+?)_", {"italic": True}),
    ]

    spans = []
    remaining = text
    while remaining:
        matched = False
        for pattern, annotations in patterns:
            match = re.search(pattern, remaining)
            if match:
                start, end = match.span()
                if start > 0:
                    spans.append({
                        "type": "text",
                        "text": {"content": remaining[:start]},
                        "annotations": {},
                    })
                spans.append({
                    "type": "text",
                    "text": {"content": match.group(1)},
                    "annotations": annotations,
                })
                remaining = remaining[end:]
                matched = True
                break
        if not matched:
            spans.append({
                "type": "text",
                "text": {"content": remaining},
                "annotations": {},
            })
            break
    return spans
