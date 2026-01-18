/**
 * DIRECT DEPLOYMENT - Bypassing Hardhat
 * Using ethers.js directly to deploy to Base Sepolia
 */

const { ethers } = require("ethers");
const fs = require("fs");
const path = require("path");

// Manual .env loading
const envPath = path.join(__dirname, ".env");
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, "utf8");
  envContent.split("\n").forEach(line => {
    const match = line.match(/^([^#=]+)=(.*)$/);
    if (match) {
      process.env[match[1].trim()] = match[2].trim();
    }
  });
}

async function main() {
  console.log("=== DIRECT DEPLOYMENT TO BASE SEPOLIA ===");

  // Read compiled contract
  const artifactPath = "./artifacts/contracts/QCI_Identity_Token.sol/QCIPhoenixProtocol.json";

  if (!fs.existsSync(artifactPath)) {
    console.error("ERROR: Contract not compiled. Run 'npx hardhat compile' first.");
    process.exit(1);
  }

  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
  console.log("Contract ABI loaded");

  // Setup provider and wallet
  const provider = new ethers.JsonRpcProvider("https://sepolia.base.org");
  const privateKey = process.env.PRIVATE_KEY;

  if (!privateKey || privateKey.length < 64) {
    console.error("ERROR: Invalid PRIVATE_KEY in .env");
    process.exit(1);
  }

  const wallet = new ethers.Wallet(privateKey, provider);
  console.log("Deployer:", wallet.address);

  const balance = await provider.getBalance(wallet.address);
  console.log("Balance:", ethers.formatEther(balance), "ETH");

  // Check vault addresses
  const treasuryAddress = process.env.TREASURY_ADDRESS;
  const ecosystemAddress = process.env.ECOSYSTEM_FUND_ADDRESS;

  if (!treasuryAddress || !ecosystemAddress) {
    console.error("ERROR: Missing TREASURY_ADDRESS or ECOSYSTEM_FUND_ADDRESS in .env");
    process.exit(1);
  }

  console.log("Treasury:", treasuryAddress);
  console.log("Ecosystem:", ecosystemAddress);

  // Deploy contract
  const MERKLE_ROOT = "0x47013a1a25f2de45e43f7755af191622cf2f2070c1b108ee034a0cf3828f697c";

  console.log("\n=== DEPLOYING ===");
  console.log("Merkle Root:", MERKLE_ROOT);

  const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, wallet);

  try {
    console.log("Sending deployment transaction...");

    const contract = await factory.deploy(
      MERKLE_ROOT,
      treasuryAddress,
      ecosystemAddress,
      {
        gasLimit: 8000000,
      }
    );

    console.log("Transaction sent:", contract.deploymentTransaction().hash);
    console.log("Waiting for confirmation...");

    await contract.waitForDeployment();

    const address = await contract.getAddress();

    console.log("\n=== DEPLOYMENT SUCCESS ===");
    console.log("Contract Address:", address);
    console.log("Explorer:", `https://sepolia.basescan.org/address/${address}`);

    // Save deployment info
    const deploymentInfo = {
      network: "base-sepolia",
      chainId: 84532,
      deployer: wallet.address,
      timestamp: new Date().toISOString(),
      contracts: {
        QCIPhoenixProtocol: address,
      },
      merkleRoot: MERKLE_ROOT,
      sovereignVaults: {
        treasury: treasuryAddress,
        ecosystem: ecosystemAddress,
      },
    };

    fs.writeFileSync("deployment-base-sepolia.json", JSON.stringify(deploymentInfo, null, 2));
    console.log("\nDeployment info saved to: deployment-base-sepolia.json");

  } catch (error) {
    console.error("\n=== DEPLOYMENT FAILED ===");
    console.error("Error:", error.message);

    if (error.code === "INSUFFICIENT_FUNDS") {
      console.error("\nINSUFFICIENT FUNDS");
      console.error("Current balance:", ethers.formatEther(balance), "ETH");
      console.error("You need more ETH. Get testnet ETH from:");
      console.error("  https://www.coinbase.com/faucets/base-ethereum-goerli-faucet");
    }

    if (error.info?.error?.message) {
      console.error("RPC Error:", error.info.error.message);
    }

    process.exit(1);
  }
}

main().catch(console.error);
