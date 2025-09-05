"""
Smart contract ABIs for Four.meme platform
"""

TOKEN_MANAGER_V2_ABI = [
    {
        "inputs": [
            {"internalType": "bytes", "name": "createArg", "type": "bytes"},
            {"internalType": "bytes", "name": "sign", "type": "bytes"}
        ],
        "name": "createToken",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "creator", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "token", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "requestId", "type": "uint256"},
            {"indexed": False, "internalType": "string", "name": "name", "type": "string"},
            {"indexed": False, "internalType": "string", "name": "symbol", "type": "string"},
            {"indexed": False, "internalType": "uint256", "name": "totalSupply", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "launchTime", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "launchFee", "type": "uint256"}
        ],
        "name": "TokenCreate",
        "type": "event"
    }
]
