"""
Main SDK class for Four.meme token creation
"""
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any

from .auth_service import AuthService
from .upload_service import UploadService
from .token_creator import TokenCreatorService
from .config import NetworkCode, CreateTokenParams

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MemeSDK:
    """
    Four.meme Token Creation SDK
    
    A complete SDK for creating tokens on the Four.meme platform
    """
    
    def __init__(self, private_key: str, network: NetworkCode = "BSC"):
        """
        Initialize the SDK
        
        Args:
            private_key: Ethereum private key (with or without 0x prefix)
            network: Network to use (BSC, ARBITRUM, or BASE)
        """
        self.private_key = private_key
        self.network = network
        
        # Initialize services
        self.auth_service = AuthService(private_key, network)
        self.upload_service = UploadService()
        self.token_creator = TokenCreatorService(private_key, network)
        
        self.is_authenticated = False
    
    def authenticate(self, wallet_name: str = "MetaMask") -> str:
        """
        Authenticate with Four.meme platform
        
        Args:
            wallet_name: Name of the wallet
            
        Returns:
            Access token
        """
        logger.info("🔐 Authenticating with Four.meme...")
        token = self.auth_service.login(wallet_name)
        self.is_authenticated = True
        logger.info("✅ Authentication successful!")
        return token
    
    def set_access_token(self, token: str):
        """
        Set access token manually (for reusing existing token)
        
        Args:
            token: Access token from previous authentication
        """
        self.auth_service.set_access_token(token)
        self.is_authenticated = True
    
    def upload_image(self, file_path: Union[str, Path]) -> str:
        """
        Upload token image from file path
        
        Args:
            file_path: Path to the image file
            
        Returns:
            URL of the uploaded image
        """
        self._require_auth()
        logger.info("📤 Uploading image...")
        return self.upload_service.upload_from_path(
            file_path, 
            self.auth_service.get_access_token()
        )
    
    def upload_image_from_url(self, image_url: str) -> str:
        """
        Upload token image from URL
        
        Args:
            image_url: URL of the image
            
        Returns:
            URL of the uploaded image on Four.meme
        """
        self._require_auth()
        logger.info("📤 Downloading and uploading image...")
        return self.upload_service.upload_from_url(
            image_url,
            self.auth_service.get_access_token()
        )
    
    def upload_image_from_bytes(self, image_bytes: bytes, filename: str) -> str:
        """
        Upload token image from bytes
        
        Args:
            image_bytes: Image data as bytes
            filename: Filename with extension
            
        Returns:
            URL of the uploaded image
        """
        self._require_auth()
        logger.info("📤 Uploading image from bytes...")
        return self.upload_service.upload_from_bytes(
            image_bytes,
            filename,
            self.auth_service.get_access_token()
        )
    
    def create_token(self, params: CreateTokenParams) -> Dict[str, Any]:
        """
        Create a new token
        
        Args:
            params: Token creation parameters
            
        Returns:
            Transaction details and token address
        """
        self._require_auth()
        
        logger.info(f"🚀 Creating token: {params.name}")
        logger.info("━" * 40)
        
        return self.token_creator.create_token(
            params,
            self.auth_service.get_access_token()
        )
    
    def create_token_with_image_upload(
        self, 
        params: CreateTokenParams,
        image_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Complete token creation flow with image upload
        
        Args:
            params: Token parameters
            image_path: Optional local image path (if not provided, uses params.image_url)
            
        Returns:
            Transaction details and token address
        """
        self._require_auth()
        
        logger.info("🎨 Starting complete token creation flow")
        logger.info("━" * 40)
        
        # Handle image upload
        if image_path:
            # Upload from local file
            logger.info("📤 Uploading image from local file...")
            params.image_url = self.upload_image(image_path)
        elif params.image_url and not params.image_url.startswith("https://static.four.meme/"):
            # Upload from external URL
            logger.info("📤 Uploading image from URL...")
            params.image_url = self.upload_image_from_url(params.image_url)
        
        # Create token
        return self.create_token(params)
    
    def get_balance(self) -> Dict[str, Any]:
        """
        Check wallet balance
        
        Returns:
            Balance information
        """
        return self.token_creator.get_balance()
    
    @property
    def address(self) -> str:
        """Get wallet address"""
        return self.auth_service.address
    
    def _require_auth(self):
        """Ensure authenticated before making requests"""
        if not self.is_authenticated or not self.auth_service.get_access_token():
            raise Exception("Not authenticated. Please call authenticate() first.")
    
    def is_logged_in(self) -> bool:
        """Check if authenticated"""
        return self.is_authenticated and self.auth_service.get_access_token() is not None
