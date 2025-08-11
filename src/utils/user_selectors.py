import re
from typing import List


def user_select_trend_from_markdown(filepath="output/final.md") -> str:
    blocks = parse_trends_from_markdown(filepath)
    
    print("\n[Trending Keyword]")
    for idx, block in enumerate(blocks):
        keyword_match = re.search(r"Keyword: (.+)", block)
        keyword = keyword_match.group(1) if keyword_match else f"List {idx+1}"
        print(f"{idx + 1}. {keyword}")

    selection = int(input("\n✅ Select the number of the trend you want: ")) - 1
    return blocks[selection].strip()


def parse_trends_from_markdown(filepath="output/final.md") -> List[str]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        blocks = re.findall(r"(## \d+\..*?)(?=\n## \d+\.|\Z)", content, re.DOTALL)
        return [block.strip() for block in blocks]
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {filepath}")
        return []
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return []
