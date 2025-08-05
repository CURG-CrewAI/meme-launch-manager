import re


def user_select_trend_from_markdown(filepath="output/final.md") -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.findall(r"(## \d+\..*?)(?=\n## \d+\.|\Z)", content, re.DOTALL)

    print("\n[Trending Keyword]")
    for idx, block in enumerate(blocks):
        keyword_match = re.search(r"Keyword: (.+)", block)
        keyword = keyword_match.group(1) if keyword_match else f"List {idx+1}"
        print(f"{idx + 1}. {keyword}")

    selection = int(input("\n✅ Select the number of the trend you want: ")) - 1
    return blocks[selection].strip()
