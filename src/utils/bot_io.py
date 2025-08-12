import re
import json
from typing import List, Dict

def parse_trends_from_json(filepath="output/trending_scraper/trends.json") -> List[Dict]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            trends = json.load(f)
        
        if isinstance(trends, list):
            return trends
        else:
            print(f"Invalid JSON format: {filepath}")
            return []
            
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return []
    except Exception as e:
        print(f"File reading error: {e}")
        return []
