"""
Token creation service for Four.meme platform
"""
import requests
import time
from web3 import Web3
from eth_account import Account
from typing import Optional, Dict, Any, Tuple
import logging

from .config import (
    NetworkCode, 
    CreateTokenParams,
    NETWORK_CONFIGS,
    API_BASE_URL,
    FIXED_TOKEN_PARAMS
)
from .abi import TOKEN_MANAGER_V2_ABI

logger = logging.getLogger(__name__)


class TokenCreatorService:
    """Handles token creation on Four.meme platform"""
    
    def __init__(self, private_key: str, network: NetworkCode = "BSC"):
        """
        Initialize token creator service
        
        Args:
            private_key: Ethereum private key
            network: Network to use
        """
        if not private_key.startswith("0x"):
            private_key = f"0x{private_key}"
        
        self.account = Account.from_key(private_key)
        self.network = network
        self.api_base_url = API_BASE_URL
        
        # Setup Web3
        config = NETWORK_CONFIGS[network]
        self.w3 = Web3(Web3.HTTPProvider(config.rpc_url))
        self.token_manager_address = config.token_manager_v2
        
        if not self.token_manager_address:
            raise ValueError(f"TokenManager V2 not available on {network}")
    
    def get_raised_token_config(self) -> Dict[str, Any]:
        """Get raised token configuration from API or use defaults"""
        try:
            response = requests.get(f"{self.api_base_url}/v1/public/config")
            response.raise_for_status()
            
            data = response.json()
            configs = data.get("data", {}).get("raisedTokens", [])
            
            # Find config for current network
            for config in configs:
                if config.get("networkCode") == self.network and config.get("symbol") == "BNB":
                    return config
        except Exception as e:
            logger.warning(f"Failed to fetch raised token config: {e}")
        
        # Return default config
        return {
            "symbol": "BNB",
            "nativeSymbol": "BNB",
            "symbolAddress": "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c",
            "deployCost": "0",
            "buyFee": "0.01",
            "sellFee": "0.01",
            "minTradeFee": "0",
            "b0Amount": "8",
            "totalBAmount": "24",
            "totalAmount": "1000000000",
            "logoUrl": "https://static.four.meme/market/68b871b6-96f7-408c-b8d0-388d804b34275092658264263839640.png",
            "tradeLevel": ["0.1", "0.5", "1"],
            "status": "PUBLISH",
            "buyTokenLink": "https://pancakeswap.finance/swap",
            "reservedNumber": 10,
            "saleRate": "0.8",
            "networkCode": self.network,
            "platform": "MEME"
        }
    
    def request_token_creation(self, params: CreateTokenParams, access_token: str) -> Tuple[str, str]:
        """
        Request token creation from API and get signature
        
        Args:
            params: Token creation parameters
            access_token: Authentication token
            
        Returns:
            Tuple of (createArg, signature)
        """
        # Get raised token config
        raised_token = self.get_raised_token_config()
        
        # Prepare request
        payload = {
            "name": params.name,
            "shortName": params.symbol,
            "desc": params.description,
            "imgUrl": params.image_url,
            "launchTime": params.launch_time or int(time.time() * 1000),
            "label": params.label.value if hasattr(params.label, 'value') else params.label,
            "webUrl": params.website,
            "twitterUrl": params.twitter,
            "telegramUrl": params.telegram,
            "preSale": params.presale_bnb,
            "raisedToken": raised_token,
            **FIXED_TOKEN_PARAMS
        }
        
        url = f"{self.api_base_url}/v1/private/token/create"
        headers = {"meme-web-access": access_token}
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") != "0":
            raise Exception(f"Failed to create token: {data.get('message', data.get('code'))}")
        
        result = data["data"]
        return result["createArg"], result["signature"]
    
    def execute_token_creation(self, create_arg: str, signature: str) -> Dict[str, Any]:
        """
        Execute token creation on blockchain
        
        Args:
            create_arg: Create argument from API
            signature: Signature from API
            
        Returns:
            Transaction receipt and token address
        """
        logger.info("Executing token creation on blockchain...")
        
        # Prepare contract
        contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.token_manager_address),
            abi=TOKEN_MANAGER_V2_ABI
        )
        
        # Convert hex strings to bytes
        create_arg_bytes = bytes.fromhex(create_arg.replace("0x", ""))
        signature_bytes = bytes.fromhex(signature.replace("0x", ""))
        
        # Build transaction
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = self.w3.eth.gas_price
        
        transaction = contract.functions.createToken(
            create_arg_bytes,
            signature_bytes
        ).build_transaction({
            'from': self.account.address,
            'nonce': nonce,
            'gas': 500000,  # Estimate or use fixed gas
            'gasPrice': gas_price,
            'value': 0  # No ETH/BNB sent with creation
        })
        
        # Sign and send transaction
        signed_txn = self.account.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        logger.info(f"Transaction submitted: {tx_hash.hex()}")
        
        # Wait for confirmation
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        logger.info(f"Transaction confirmed: {receipt['status']}")
        
        # Parse events to get token address
        token_address = None
        if receipt['status'] == 1:
            # Parse TokenCreate event
            contract_events = contract.events.TokenCreate().process_receipt(receipt)
            if contract_events:
                token_address = contract_events[0]['args']['token']
                logger.info(f"Token created at address: {token_address}")
        
        return {
            "transaction_hash": tx_hash.hex(),
            "token_address": token_address,
            "status": receipt['status'],
            "gas_used": receipt['gasUsed']
        }
    
    def create_token(self, params: CreateTokenParams, access_token: str) -> Dict[str, Any]:
        """
        Complete token creation flow
        
        Args:
            params: Token creation parameters
            access_token: Authentication token
            
        Returns:
            Transaction details and token address
        """
        try:
            logger.info(f"Starting token creation: {params.name} ({params.symbol})")
            
            # Step 1: Get signature from API
            logger.info("Requesting token creation from API...")
            create_arg, signature = self.request_token_creation(params, access_token)
            logger.info("API signature received")
            
            # Step 2: Execute on blockchain
            logger.info("Executing on blockchain...")
            result = self.execute_token_creation(create_arg, signature)
            
            logger.info("Token creation completed!")
            
            return {
                **result,
                "token_info": {
                    "name": params.name,
                    "symbol": params.symbol,
                    "label": params.label
                }
            }
            
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            raise
    
    def get_balance(self) -> Dict[str, Any]:
        """Get wallet balance"""
        balance_wei = self.w3.eth.get_balance(self.account.address)
        balance_bnb = self.w3.from_wei(balance_wei, 'ether')
        
        return {
            "address": self.account.address,
            "balance_wei": balance_wei,
            "balance_bnb": float(balance_bnb),
            "formatted": f"{balance_bnb:.4f} BNB"
        }
