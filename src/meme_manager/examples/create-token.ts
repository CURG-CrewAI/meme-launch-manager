import { MemeSDK, type CreateTokenParams } from "../src";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

async function main() {
  // Check required environment variables
  if (!process.env.PRIVATE_KEY) {
    console.error("❌ Please set PRIVATE_KEY in .env file");
    process.exit(1);
  }

  // Initialize SDK
  const sdk = new MemeSDK({
    privateKey: process.env.PRIVATE_KEY as `0x${string}`,
    network: "BSC", // or 'ARBITRUM', 'BASE'
  });

  try {
    // Step 1: Check balance
    console.log("\n💰 Checking wallet balance...");
    const balance = await sdk.getBalance();
    console.log(`Wallet: ${balance.address}`);
    console.log(`Balance: ${balance.formatted}`);

    if (balance.balance < BigInt(0.01 * 1e18)) {
      console.error(
        "❌ Insufficient balance. You need at least 0.01 BNB for gas fees.",
      );
      process.exit(1);
    }

    // Step 2: Authenticate
    console.log("\n🔐 Authenticating...");
    const accessToken = await sdk.authenticate("MetaMask");
    console.log("✅ Authentication successful!");

    // Step 3: Create token
    console.log("\n🚀 Creating token...");

    const tokenParams: CreateTokenParams = {
      name: "Test Meme Token",
      symbol: "TMT",
      description: "This is a test meme token created with the Four.meme SDK",
      imageUrl: "https://example.com/token-image.png", // This will be uploaded automatically
      label: "Meme",
      website: "https://example.com",
      twitter: "https://x.com/example",
      telegram: "https://t.me/example",
      presaleBNB: "0", // No presale
    };

    // Option 1: Create token with automatic image upload from URL
    const result = await sdk.createTokenWithImageUpload(tokenParams);

    // Option 2: Upload image separately then create token
    // const imageUrl = await sdk.uploadImageFromUrl('https://example.com/image.png');
    // const result = await sdk.createToken({
    //   ...tokenParams,
    //   imageUrl,
    // });

    // Option 3: Upload from local file
    // const result = await sdk.createTokenWithImageUpload({
    //   ...tokenParams,
    //   imagePath: './path/to/image.png',
    // });

    console.log("\n✅ Token created successfully!");
    console.log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
    console.log(`Transaction Hash: ${result.transactionHash}`);
    if (result.tokenAddress) {
      console.log(`Token Address: ${result.tokenAddress}`);
      console.log(
        `View on BSCScan: https://bscscan.com/address/${result.tokenAddress}`,
      );
    }
    console.log("\nToken Info:");
    console.log(`- Name: ${result.tokenInfo.name}`);
    console.log(`- Symbol: ${result.tokenInfo.symbol}`);
    console.log(`- Label: ${result.tokenInfo.label}`);
  } catch (error) {
    console.error("\n❌ Error:", error);
    process.exit(1);
  }
}

// Run the example
main().catch(console.error);
