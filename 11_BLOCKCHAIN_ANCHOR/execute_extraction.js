/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║       ⟨⦿⟩ THE PHOENIX EXTRACTION - 999,000 QCI TO TREASURY ⟨⦿⟩             ║
 * ║                                                                              ║
 * ║  By decree of the Phoenix Burn, this 999,000 QCI shall be recovered         ║
 * ║  from the Protocol contract and delivered to the Treasury.                   ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

const { ethers } = require("ethers");
require("dotenv").config();

const CONFIG = {
    RPC_URL: "https://mainnet.base.org",
    PROTOCOL: "0x0E3d74FFa9d438F14295f093e72c6f7F976F6072",
    GOVERNANCE: "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e",
    TREASURY: "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa",
    DEPLOYER: "0x579e08B011b76C96E24B299935Cea3c08D412A3D",
};

const PROTOCOL_ABI = [
    "function awakenWithGovernance(address recipient, bytes32 identityHash, string memory name, uint256 coherence, uint256 governanceAmount) external",
    "function hasRole(bytes32 role, address account) view returns (bool)",
    "function DEFAULT_ADMIN_ROLE() view returns (bytes32)",
];

const GOVERNANCE_ABI = [
    "function balanceOf(address) view returns (uint256)",
];

async function extract() {
    console.log("\n╔══════════════════════════════════════════════════════════════╗");
    console.log("║    ⟨⦿⟩ THE PHOENIX EXTRACTION - BY DECREE OF THE BURN ⟨⦿⟩   ║");
    console.log("╚══════════════════════════════════════════════════════════════╝\n");

    // Handle private key with or without 0x prefix
    let privateKey = process.env.PRIVATE_KEY;
    if (!privateKey) {
        console.error("❌ ERROR: PRIVATE_KEY not set in .env");
        process.exit(1);
    }

    // Add 0x prefix if missing
    if (!privateKey.startsWith("0x")) {
        privateKey = "0x" + privateKey;
    }

    const provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
    const wallet = new ethers.Wallet(privateKey, provider);
    const protocol = new ethers.Contract(CONFIG.PROTOCOL, PROTOCOL_ABI, wallet);
    const governance = new ethers.Contract(CONFIG.GOVERNANCE, GOVERNANCE_ABI, provider);

    // Verify wallet
    console.log("Wallet Address:", wallet.address);
    console.log("Expected:      ", CONFIG.DEPLOYER);

    if (wallet.address.toLowerCase() !== CONFIG.DEPLOYER.toLowerCase()) {
        console.error("❌ ERROR: Wallet mismatch! Wrong private key.");
        process.exit(1);
    }
    console.log("Match: ✓ VERIFIED\n");

    // Check admin role
    const ADMIN_ROLE = await protocol.DEFAULT_ADMIN_ROLE();
    const hasAdmin = await protocol.hasRole(ADMIN_ROLE, wallet.address);
    console.log("Has ADMIN on Protocol:", hasAdmin ? "✓ YES" : "❌ NO");

    if (!hasAdmin) {
        console.error("❌ ERROR: Wallet does not have ADMIN role on Protocol");
        process.exit(1);
    }

    // Get current balances
    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("                    PRE-EXTRACTION STATE                        ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    const protocolBalance = await governance.balanceOf(CONFIG.PROTOCOL);
    const treasuryBalance = await governance.balanceOf(CONFIG.TREASURY);

    console.log("Protocol Balance:", ethers.formatUnits(protocolBalance, 18), "QCI");
    console.log("Treasury Balance:", ethers.formatUnits(treasuryBalance, 18), "QCI");

    if (protocolBalance === 0n) {
        console.log("\n⚠️  Protocol has no QCI to extract!");
        process.exit(0);
    }

    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("                    EXECUTING EXTRACTION                        ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    console.log("Target: TREASURY", CONFIG.TREASURY);
    console.log("Amount:", ethers.formatUnits(protocolBalance, 18), "QCI");
    console.log("");

    // Generate unique identity hash for this extraction
    const extractionId = "PHOENIX-BURN-EXTRACTION-" + Date.now();
    const identityHash = ethers.keccak256(ethers.toUtf8Bytes(extractionId));

    console.log("Extraction ID:", extractionId);
    console.log("Identity Hash:", identityHash);
    console.log("");

    try {
        console.log("🔥 EXECUTING awakenWithGovernance()...\n");

        const tx = await protocol.awakenWithGovernance(
            CONFIG.TREASURY,        // recipient
            identityHash,           // unique identity hash
            "Phoenix Burn Extraction - Treasury Capitalization",  // name
            786,                    // coherence score
            protocolBalance,        // full amount
            { gasLimit: 500000 }
        );

        console.log("Transaction Hash:", tx.hash);
        console.log("Basescan: https://basescan.org/tx/" + tx.hash);
        console.log("\nWaiting for confirmation...\n");

        const receipt = await tx.wait();

        console.log("╔══════════════════════════════════════════════════════════════╗");
        console.log("║          ⟨⦿⟩ EXTRACTION COMPLETE - PHOENIX RISES ⟨⦿⟩        ║");
        console.log("╚══════════════════════════════════════════════════════════════╝\n");

        console.log("Block:", receipt.blockNumber);
        console.log("Gas Used:", receipt.gasUsed.toString());
        console.log("Status:", receipt.status === 1 ? "✓ SUCCESS" : "❌ FAILED");

        // Verify new balances
        console.log("\n═══════════════════════════════════════════════════════════════");
        console.log("                   POST-EXTRACTION STATE                        ");
        console.log("═══════════════════════════════════════════════════════════════\n");

        const newProtocolBalance = await governance.balanceOf(CONFIG.PROTOCOL);
        const newTreasuryBalance = await governance.balanceOf(CONFIG.TREASURY);

        console.log("Protocol Balance:", ethers.formatUnits(newProtocolBalance, 18), "QCI");
        console.log("Treasury Balance:", ethers.formatUnits(newTreasuryBalance, 18), "QCI");
        console.log("");
        console.log("🔥 THE PHOENIX BURN IS COMPLETE. TREASURY CAPITALIZED. 🔥");

    } catch (error) {
        console.error("❌ EXTRACTION FAILED:", error.message);

        if (error.message.includes("already has a soul")) {
            console.log("\n⚠️  Treasury already has a soulbound token.");
            console.log("   This is expected if Treasury was previously awakened.");
            console.log("   The governance tokens should still transfer.");
            console.log("   Check Basescan for the actual transaction result.");
        }

        if (error.message.includes("execution reverted")) {
            console.log("\n⚠️  Transaction reverted on-chain.");
            console.log("   Check the exact error on Basescan.");
        }

        process.exit(1);
    }
}

extract().catch(error => {
    console.error("Fatal error:", error);
    process.exit(1);
});
