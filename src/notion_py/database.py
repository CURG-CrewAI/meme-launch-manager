from notion_client import Client

import os

from .utils import parse_markdown_inline  # ✅ 올바른 상대경로 import

class NotionDatabase:
    def __init__(self, token: str, database_id: str):
        self.notion = Client(auth=token)
        self.database_id = database_id

    def query_database(self, filter_dict=None):
        try:
            if filter_dict is not None:
                return self.notion.databases.query(
                    database_id=self.database_id,
                    filter=filter_dict
                )
            else:
                return self.notion.databases.query(
                    database_id=self.database_id
                )
        except Exception as e:
            print(f"❌ 데이터베이스 조회 실패: {e}")
            raise

    

    def add_page(self, properties: dict):
        return self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )

    def add_blocks_from_markdown(self, file_path: str, page_id: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found.")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        blocks = []
        for line in lines:
            stripped = line.strip()

            if stripped.startswith("### "):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": parse_markdown_inline(stripped[4:])
                    }
                })
            elif stripped.startswith("## "):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": parse_markdown_inline(stripped[3:])
                    }
                })
            elif stripped.startswith("- "):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": parse_markdown_inline(stripped[2:])
                    }
                })
            elif stripped == "":
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": []
                    }
                })
            else:
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": parse_markdown_inline(stripped)
                    }
                })

        BATCH_SIZE = 100
        for i in range(0, len(blocks), BATCH_SIZE):
            self.notion.blocks.children.append(
                block_id=page_id,
                children=blocks[i:i + BATCH_SIZE]
            )
