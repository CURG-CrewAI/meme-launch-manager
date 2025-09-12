import os
import requests
from typing import Dict, Any

WORKER_URL = os.environ["WORKER_URL"]


def add_domain(project_name: str) -> Dict[str, Any]:
    """Add Domain"""
    worker_url = WORKER_URL
    try:
        response = requests.post(
            worker_url,
            json={
                "project_name": project_name,
            },
            timeout=30,
        )

        result = response.json()
        print(result)

        if result.get("success"):
            return result["domain"]
        else:
            return "error"

    except Exception as e:
        return "network error"
