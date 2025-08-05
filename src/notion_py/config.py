from dotenv import load_dotenv
import os


load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")

if NOTION_API_KEY is None or DATABASE_ID is None:
    raise ValueError("The environment variables NOTION_API_KEY or DATABASE_ID have not been set.")
