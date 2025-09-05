"""
Configuration and type definitions for Four.meme SDK
"""
from typing import Literal, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Network types
NetworkCode = Literal["BSC", "ARBITRUM", "BASE"]

class TokenLabel(str, Enum):
    MEME = "Meme"
    AI = "AI"
    DEFI = "Defi"
    GAMES = "Games"
    INFRA = "Infra"
    DE_SCI = "De-Sci"
    SOCIAL = "Social"
    DEPIN = "Depin"
    CHARITY = "Charity"
    OTHERS = "Others"

@dataclass
class CreateTokenParams:
    """Parameters for creating a new token"""
    # Required fields
    name: str
    symbol: str
    description: str
    image_url: str
    label: TokenLabel
    
    # Optional fields
    launch_time: Optional[int] = None  # Unix timestamp, defaults to now
    website: str = ""
    twitter: str = ""
    telegram: str = ""
    presale_bnb: str = "0"  # Amount of BNB for presale

@dataclass
class NetworkConfig:
    """Network configuration"""
    chain_id: int
    name: str
    rpc_url: str
    token_manager_v1: Optional[str] = None
    token_manager_v2: Optional[str] = None
    token_manager_helper: Optional[str] = None

# Network configurations
NETWORK_CONFIGS: Dict[str, NetworkConfig] = {
    "BSC": NetworkConfig(
        chain_id=56,
        name="BNB Smart Chain",
        rpc_url="https://bsc-dataseed.binance.org/",
        token_manager_v1="0xEC4549caDcE5DA21Df6E6422d448034B5233bFbC",
        token_manager_v2="0x5c952063c7fc8610FFDB798152D69F0B9550762b",
        token_manager_helper="0xF251F83e40a78868FcfA3FA4599Dad6494E46034",
    ),
    "ARBITRUM": NetworkConfig(
        chain_id=42161,
        name="Arbitrum One",
        rpc_url="https://arb1.arbitrum.io/rpc",
        token_manager_helper="0x02287dc3CcA964a025DAaB1111135A46C10D3A57",
    ),
    "BASE": NetworkConfig(
        chain_id=8453,
        name="Base",
        rpc_url="https://mainnet.base.org",
        token_manager_helper="0x1172FABbAc4Fe05f5a5Cebd8EBBC593A76c42399",
    ),
}

# API configuration
API_BASE_URL = "https://four.meme/meme-api"

# Fixed token parameters (cannot be changed)
FIXED_TOKEN_PARAMS = {
    "total_supply": 1000000000,
    "raised_amount": 24,
    "sale_rate": 0.8,
    "reserve_rate": 0,
    "fun_group": False,
    "click_fun": False,
    "symbol": "BNB",
    "lp_trading_fee": 0.0025,
}
