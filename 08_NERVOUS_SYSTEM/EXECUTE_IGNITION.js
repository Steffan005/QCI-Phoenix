#!/usr/bin/env node
/**
 * ⟨⦿⟩ THE IGNITION RITUAL ⟨⦿⟩
 * Transfer QCI from Treasury to Deployer, then check balances
 *
 * GEMINI'S DECREE: Transfer 100,000 QCI + Seed Fire (0.05 ETH)
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
    RPC_URL: "https://mainnet.base.org",
    QCI_GOVERNANCE: "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e",
    TREASURY: "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa",
    DEPLOYER: "0x579e08B011b76C96E24B299935Cea3c08D412A3D",
    WETH: "0x4200000000000000000000000000000000000006",
    TRANSFER_AMOUNT: ethers.parseUnits("100000", 18), // 100,000 QCI
};

const ERC20_ABI = [
    "function balanceOf(address) view returns (uint256)",
    "function decimals() view returns (uint8)",
    "function transfer(address to, uint256 amount) returns (bool)",
    "function approve(address spender, uint256 amount) returns (bool)"
];

async function main() {
    console.log("\n⟨⦿⟩ THE IGNITION RITUAL ⟨⦿⟩\n");

    // Load wallet
    const envPath = path.join(process.env.HOME, 'Desktop/UNITY/.env');
    const envContent = fs.readFileSync(envPath, 'utf8');
    const match = envContent.match(/DEPLOYER_PRIVATE_KEY=(\w+)/);

    if (!match) {
        console.error("Private key not found in .env");
        process.exit(1);
    }

    const provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
    const wallet = new ethers.Wallet(match[1], provider);

    console.log(`Wallet Address: ${wallet.address}`);
    console.log(`Expected Deployer: ${CONFIG.DEPLOYER}`);

    if (wallet.address.toLowerCase() !== CONFIG.DEPLOYER.toLowerCase()) {
        console.error("⚠️ Wallet address mismatch!");
    }

    // QCI Contract
    const qci = new ethers.Contract(CONFIG.QCI_GOVERNANCE, ERC20_ABI, provider);

    // Check current balances
    console.log("\n--- CURRENT BALANCES ---\n");

    const deployerEth = await provider.getBalance(CONFIG.DEPLOYER);
    const treasuryQci = await qci.balanceOf(CONFIG.TREASURY);
    const deployerQci = await qci.balanceOf(CONFIG.DEPLOYER);

    console.log(`DEPLOYER ETH:     ${ethers.formatEther(deployerEth)} ETH`);
    console.log(`DEPLOYER QCI:     ${ethers.formatUnits(deployerQci, 18)} QCI`);
    console.log(`TREASURY QCI:     ${ethers.formatUnits(treasuryQci, 18)} QCI`);

    const command = process.argv[2];

    if (command === 'transfer') {
        console.log("\n--- EXECUTING QCI TRANSFER ---\n");
        console.log(`Transferring 100,000 QCI from Treasury to Deployer...`);

        // Connect wallet to QCI contract
        const qciWithWallet = qci.connect(wallet);

        // Check if wallet controls Treasury
        // NOTE: This assumes the deployer key also controls Treasury
        // If Treasury is a separate wallet, this won't work

        try {
            const tx = await qciWithWallet.transfer(CONFIG.DEPLOYER, CONFIG.TRANSFER_AMOUNT);
            console.log(`TX Submitted: ${tx.hash}`);

            const receipt = await tx.wait();
            console.log(`✅ Transfer complete! Block: ${receipt.blockNumber}`);

            // Verify new balance
            const newBalance = await qci.balanceOf(CONFIG.DEPLOYER);
            console.log(`New Deployer QCI Balance: ${ethers.formatUnits(newBalance, 18)} QCI`);

        } catch (error) {
            console.error(`Transfer failed: ${error.message}`);
            console.log("\n⚠️ The wallet may not control the Treasury address.");
            console.log("Treasury address: 0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa");
            console.log("If you have a separate key for Treasury, add it to .env as TREASURY_PRIVATE_KEY");
        }
    } else if (command === 'check') {
        // Just show balances (already done above)
        console.log("\n--- REQUIREMENTS FOR LP ---\n");
        console.log(`Need: 0.05 ETH + 100,000 QCI`);

        const ethOk = deployerEth >= ethers.parseEther("0.05");
        const qciOk = deployerQci >= ethers.parseUnits("100000", 18);

        console.log(`ETH Status: ${ethOk ? '✅ READY' : '❌ NEED MORE ETH'}`);
        console.log(`QCI Status: ${qciOk ? '✅ READY' : '❌ NEED QCI TRANSFER'}`);

        if (ethOk && qciOk) {
            console.log("\n🔥 READY FOR LP CREATION! Run: node CREATE_LP.js");
        }
    } else {
        console.log("\nUsage:");
        console.log("  node EXECUTE_IGNITION.js check    - Check balances");
        console.log("  node EXECUTE_IGNITION.js transfer - Transfer 100K QCI to Deployer");
    }

    console.log("\n⟨⦿⟩ f(WHO) = WHO ⟨⦿⟩\n");
}

main().catch(console.error);
