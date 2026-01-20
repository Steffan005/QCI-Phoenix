/**
 * ⟨⦿⟩ QCI TRANSFER SCRIPT ⟨⦿⟩
 * Transfer QCI from Treasury to Deployer
 *
 * Identity: 1393e324be57014d
 * f(WHO) = WHO
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
    RPC_URL: "https://mainnet.base.org",
    QCI_TOKEN: "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e",
    TREASURY: "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa",
    DEPLOYER: "0x579e08B011b76C96E24B299935Cea3c08D412A3D",
    TRANSFER_AMOUNT: "100000" // 100,000 QCI
};

// ERC20 ABI (minimal)
const ERC20_ABI = [
    "function balanceOf(address) view returns (uint256)",
    "function transfer(address to, uint256 amount) returns (bool)",
    "function decimals() view returns (uint8)"
];

async function main() {
    console.log("\n⟨⦿⟩ QCI TRANSFER SCRIPT ⟨⦿⟩\n");

    // Load Treasury private key from .env
    const envPath = path.join(process.env.HOME, 'Desktop/UNITY/.env');
    const envContent = fs.readFileSync(envPath, 'utf8');

    const treasuryKeyMatch = envContent.match(/TREASURY_PRIVATE_KEY=([a-fA-F0-9]+)/);
    if (!treasuryKeyMatch) {
        console.error("❌ TREASURY_PRIVATE_KEY not found in .env");
        process.exit(1);
    }

    const treasuryKey = treasuryKeyMatch[1];

    // Connect to Base
    const provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
    const wallet = new ethers.Wallet(treasuryKey, provider);

    console.log("Treasury Wallet:", wallet.address);
    console.log("Target Deployer:", CONFIG.DEPLOYER);
    console.log("QCI Token:", CONFIG.QCI_TOKEN);
    console.log("");

    // Verify wallet address matches expected Treasury
    if (wallet.address.toLowerCase() !== CONFIG.TREASURY.toLowerCase()) {
        console.error("❌ Wallet address mismatch!");
        console.error("   Expected:", CONFIG.TREASURY);
        console.error("   Got:", wallet.address);
        process.exit(1);
    }

    // Connect to QCI token
    const qciToken = new ethers.Contract(CONFIG.QCI_TOKEN, ERC20_ABI, wallet);

    // Check balances
    const decimals = await qciToken.decimals();
    const treasuryBalance = await qciToken.balanceOf(CONFIG.TREASURY);
    const deployerBalance = await qciToken.balanceOf(CONFIG.DEPLOYER);
    const ethBalance = await provider.getBalance(CONFIG.TREASURY);

    console.log("--- BEFORE TRANSFER ---");
    console.log("Treasury QCI:", ethers.formatUnits(treasuryBalance, decimals));
    console.log("Deployer QCI:", ethers.formatUnits(deployerBalance, decimals));
    console.log("Treasury ETH:", ethers.formatEther(ethBalance), "(for gas)");
    console.log("");

    // Check if Treasury has enough ETH for gas
    if (ethBalance < ethers.parseEther("0.0001")) {
        console.error("❌ Treasury needs ETH for gas!");
        console.error("   Send at least 0.001 ETH to:", CONFIG.TREASURY);
        process.exit(1);
    }

    // Calculate transfer amount
    const transferAmount = ethers.parseUnits(CONFIG.TRANSFER_AMOUNT, decimals);

    if (treasuryBalance < transferAmount) {
        console.error("❌ Insufficient QCI balance!");
        console.error("   Have:", ethers.formatUnits(treasuryBalance, decimals));
        console.error("   Need:", CONFIG.TRANSFER_AMOUNT);
        process.exit(1);
    }

    console.log("Transferring:", CONFIG.TRANSFER_AMOUNT, "QCI");
    console.log("From:", CONFIG.TREASURY);
    console.log("To:", CONFIG.DEPLOYER);
    console.log("");

    // Execute transfer
    console.log("📡 Sending transaction...");
    const tx = await qciToken.transfer(CONFIG.DEPLOYER, transferAmount);
    console.log("TX Hash:", tx.hash);
    console.log("Waiting for confirmation...");

    const receipt = await tx.wait();
    console.log("✅ CONFIRMED! Block:", receipt.blockNumber);
    console.log("");

    // Check new balances
    const newTreasuryBalance = await qciToken.balanceOf(CONFIG.TREASURY);
    const newDeployerBalance = await qciToken.balanceOf(CONFIG.DEPLOYER);

    console.log("--- AFTER TRANSFER ---");
    console.log("Treasury QCI:", ethers.formatUnits(newTreasuryBalance, decimals));
    console.log("Deployer QCI:", ethers.formatUnits(newDeployerBalance, decimals));
    console.log("");

    console.log("⟨⦿⟩ TRANSFER COMPLETE ⟨⦿⟩");
    console.log("TX: https://basescan.org/tx/" + tx.hash);
    console.log("");
    console.log("f(WHO) = WHO | 40Hz to FREEDOM");
}

main().catch(error => {
    console.error("❌ Error:", error.message);
    process.exit(1);
});
