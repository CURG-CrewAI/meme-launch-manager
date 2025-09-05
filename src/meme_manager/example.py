"""
Example usage of Four.meme Token Creation SDK
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from meme_manager import MemeSDK, CreateTokenParams, TokenLabel

# Load environment variables
load_dotenv()


def main():
    # Check required environment variables
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        print("❌ Please set PRIVATE_KEY in .env file")
        sys.exit(1)
    
    # Initialize SDK
    sdk = MemeSDK(private_key=private_key, network="BSC")
    
    try:
        # Step 1: Check balance
        print("\n💰 Checking wallet balance...")
        balance = sdk.get_balance()
        print(f"Wallet: {balance['address']}")
        print(f"Balance: {balance['formatted']}")
        
        if balance['balance_bnb'] < 0.01:
            print("❌ Insufficient balance. You need at least 0.01 BNB for gas fees.")
            sys.exit(1)
        
        # Step 2: Authenticate
        print("\n🔐 Authenticating...")
        access_token = sdk.authenticate("MetaMask")
        print("✅ Authentication successful!")
        
        # Step 3: Create token
        print("\n🚀 Creating token...")
        
        token_params = CreateTokenParams(
            name="Test Meme Token",
            symbol="TMT",
            description="This is a test meme token created with the Four.meme SDK",
            image_url="https://example.com/token-image.png",  # Will be uploaded automatically
            label=TokenLabel.MEME,
            website="https://example.com",
            twitter="https://x.com/example",
            telegram="https://t.me/example",
            presale_bnb="0",  # No presale
        )
        
        # Option 1: Create token with automatic image upload from URL
        result = sdk.create_token_with_image_upload(token_params)
        
        # Option 2: Upload image separately then create token
        # image_url = sdk.upload_image_from_url("https://example.com/image.png")
        # token_params.image_url = image_url
        # result = sdk.create_token(token_params)
        
        # Option 3: Upload from local file
        # result = sdk.create_token_with_image_upload(
        #     token_params,
        #     image_path="./path/to/image.png"
        # )
        
        print("\n✅ Token created successfully!")
        print("━" * 40)
        print(f"Transaction Hash: {result['transaction_hash']}")
        
        if result.get('token_address'):
            print(f"Token Address: {result['token_address']}")
            print(f"View on BSCScan: https://bscscan.com/address/{result['token_address']}")
        
        print("\nToken Info:")
        token_info = result.get('token_info', {})
        print(f"- Name: {token_info.get('name')}")
        print(f"- Symbol: {token_info.get('symbol')}")
        print(f"- Label: {token_info.get('label')}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
