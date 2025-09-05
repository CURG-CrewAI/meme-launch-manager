"""
Image upload service for Four.meme platform
"""
import requests
import os
from pathlib import Path
from typing import Optional, Union
import logging
from io import BytesIO

from .config import API_BASE_URL

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}


class UploadService:
    """Handles image uploads to Four.meme platform"""
    
    def __init__(self):
        self.api_base_url = API_BASE_URL
    
    def upload_from_path(self, file_path: Union[str, Path], access_token: str) -> str:
        """
        Upload image from local file path
        
        Args:
            file_path: Path to the image file
            access_token: Authentication token
            
        Returns:
            URL of the uploaded image
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file extension
        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Upload file
        url = f"{self.api_base_url}/v1/private/token/upload"
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'image/jpeg')}
            headers = {'meme-web-access': access_token}
            
            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") != "0":
                raise Exception(f"Failed to upload image: {data.get('message', data.get('code'))}")
            
            logger.info(f"Image uploaded successfully: {data['data']}")
            return data["data"]
    
    def upload_from_url(self, image_url: str, access_token: str) -> str:
        """
        Download image from URL and upload to Four.meme
        
        Args:
            image_url: URL of the image to download
            access_token: Authentication token
            
        Returns:
            URL of the uploaded image on Four.meme platform
        """
        try:
            logger.info(f"Downloading image from: {image_url}")
            
            # Download image
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            # Get filename from URL or use default
            filename = os.path.basename(image_url.split('?')[0])
            if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                # Try to determine extension from content-type
                content_type = response.headers.get('content-type', '')
                ext_map = {
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'image/bmp': '.bmp',
                    'image/webp': '.webp',
                }
                ext = ext_map.get(content_type, '.jpg')
                filename = f"image_{hash(image_url)}{ext}"
            
            # Upload to Four.meme
            url = f"{self.api_base_url}/v1/private/token/upload"
            
            files = {'file': (filename, BytesIO(response.content), 'image/jpeg')}
            headers = {'meme-web-access': access_token}
            
            upload_response = requests.post(url, files=files, headers=headers)
            upload_response.raise_for_status()
            
            data = upload_response.json()
            if data.get("code") != "0":
                raise Exception(f"Failed to upload image: {data.get('message', data.get('code'))}")
            
            logger.info(f"Image uploaded successfully: {data['data']}")
            return data["data"]
            
        except Exception as e:
            logger.error(f"Error uploading image from URL: {e}")
            raise
    
    def upload_from_bytes(self, image_bytes: bytes, filename: str, access_token: str) -> str:
        """
        Upload image from bytes
        
        Args:
            image_bytes: Image data as bytes
            filename: Filename with extension
            access_token: Authentication token
            
        Returns:
            URL of the uploaded image
        """
        # Check file extension
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # Upload file
        url = f"{self.api_base_url}/v1/private/token/upload"
        
        files = {'file': (filename, BytesIO(image_bytes), 'image/jpeg')}
        headers = {'meme-web-access': access_token}
        
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") != "0":
            raise Exception(f"Failed to upload image: {data.get('message', data.get('code'))}")
        
        logger.info(f"Image uploaded successfully: {data['data']}")
        return data["data"]
