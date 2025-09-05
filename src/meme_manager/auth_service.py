"""
Authentication service for Four.meme platform
"""
import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from typing import Optional
import logging

from .config import NetworkCode, API_BASE_URL

logger = logging.getLogger(__name__)


class AuthService:
    """Handles authentication with Four.meme platform"""
    
    def __init__(self, private_key: str, network: NetworkCode = "BSC"):
        """
        Initialize authentication service
        
        Args:
            private_key: Ethereum private key (with or without 0x prefix)
            network: Network to use (BSC, ARBITRUM, or BASE)
        """
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        
        self.account = Account.from_key(private_key)
        self.network = network
        self.access_token: Optional[str] = None
        self.api_base_url = API_BASE_URL
    
    def generate_nonce(self) -> str:
        """Generate nonce for login"""
        url = f"{self.api_base_url}/v1/private/user/nonce/generate"
        
        payload = {
            "accountAddress": self.account.address,
            "verifyType": "LOGIN",
            "networkCode": self.network,
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") != "0":
            raise Exception(f"Failed to generate nonce: {data.get('message', data.get('code'))}")
        
        return data["data"]
    
    def sign_message(self, nonce: str) -> str:
        """Sign the login message"""
        message = f"You are sign in Meme {nonce}"
        message_hash = encode_defunct(text=message)
        signed_message = self.account.sign_message(message_hash)
        return signed_message.signature.hex()
    
    def login(self, wallet_name: str = "MetaMask") -> str:
        """
        Perform login and get access token
        
        Args:
            wallet_name: Name of the wallet (default: MetaMask)
            
        Returns:
            Access token for authenticated requests
        """
        try:
            # Step 1: Generate nonce
            logger.info("Generating nonce...")
            nonce = self.generate_nonce()
            logger.info(f"Nonce generated: {nonce}")
            
            # Step 2: Sign message
            logger.info("Signing login message...")
            signature = self.sign_message(nonce)
            
            # Step 3: Login
            logger.info("Logging in...")
            url = f"{self.api_base_url}/v1/private/user/login/dex"
            
            payload = {
                "region": "WEB",
                "langType": "EN",
                "loginIp": "",
                "inviteCode": "",
                "verifyInfo": {
                    "address": self.account.address,
                    "networkCode": self.network,
                    "signature": signature,
                    "verifyType": "LOGIN",
                },
                "walletName": wallet_name,
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") != "0":
                raise Exception(f"Login failed: {data.get('message', data.get('code'))}")
            
            self.access_token = data["data"]
            logger.info("Login successful!")
            
            return self.access_token
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise
    
    def get_access_token(self) -> Optional[str]:
        """Get current access token"""
        return self.access_token
    
    def set_access_token(self, token: str):
        """Set access token manually (for reuse)"""
        self.access_token = token
    
    @property
    def address(self) -> str:
        """Get wallet address"""
        return self.account.address
