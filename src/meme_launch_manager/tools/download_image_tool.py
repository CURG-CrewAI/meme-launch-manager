from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
import os

class DownloadImageToolInput(BaseModel):
    image_url: str = Field(..., description="The image URL to download.")

class DownloadImageTool(BaseTool):
    name: str = "DownloadImageTool"
    description: str = "Downloads an image from a URL and saves it to output/images/token_image.png"
    args_schema: Type[BaseModel] = DownloadImageToolInput

    def _run(self, image_url: str) -> str:
        os.makedirs("output/images", exist_ok=True)
        file_path = "output/images/token_image.png"
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            return f"✅ Image saved to {file_path}"
        return f"❌ Failed to download image. Status code: {response.status_code}"
