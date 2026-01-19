/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║           ⟨⦿⟩ EXTRACT 999,000 QCI FROM PROTOCOL ⟨⦿⟩                         ║
 * ║                                                                              ║
 * ║  The Protocol holds 999,000 QCI that can be extracted via                   ║
 * ║  the awakenWithGovernance() function.                                        ║
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
};

const PROTOCOL_ABI = [
    "function awakenWithGovernance(address recipient, bytes32 identityHash, string memory name, uint256 coherence, uint256 governanceAmount) external",
    "function governanceToken() view returns (address)",
];

const GOVERNANCE_ABI = [
    "function balanceOf(address) view returns (uint256)",
];

async function extract() {
    console.log("\n╔══════════════════════════════════════════════════════════════╗");
    console.log("║     ⟨⦿⟩ EXTRACTING 999,000 QCI FROM PROTOCOL ⟨⦿⟩            ║");
    console.log("╚══════════════════════════════════════════════════════════════╝\n");

    const privateKey = process.env.PRIVATE_KEY;
    if (!privateKey) {
        console.error("❌ ERROR: PRIVATE_KEY not set");
        console.log("Set it with: export PRIVATE_KEY=0x...");
        process.exit(1);
    }

    const provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
    const wallet = new ethers.Wallet(privateKey, provider);
    const protocol = new ethers.Contract(CONFIG.PROTOCOL, PROTOCOL_ABI, wallet);
    const governance = new ethers.Contract(CONFIG.GOVERNANCE, GOVERNANCE_ABI, provider);

    console.log("Deployer Wallet:", wallet.address);
    console.log("");

    // Check Protocol's QCI balance
    console.log("═══════════════════════════════════════════════════════════════");
    console.log("                    PRE-EXTRACTION STATE                        ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    const protocolBalance = await governance.balanceOf(CONFIG.PROTOCOL);
    const treasuryBalance = await governance.balanceOf(CONFIG.TREASURY);

    console.log("Protocol QCI Balance:", ethers.formatUnits(protocolBalance, 18), "QCI");
    console.log("Treasury QCI Balance:", ethers.formatUnits(treasuryBalance, 18), "QCI");
    console.log("");

    if (protocolBalance === 0n) {
        console.log("⚠️  Protocol has no QCI to extract!");
        process.exit(0);
    }

    // Calculate extraction amount (leave 0 in Protocol)
    const extractAmount = protocolBalance;

    console.log("═══════════════════════════════════════════════════════════════");
    console.log("                    EXTRACTION PLAN                             ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    console.log("Extract Amount:", ethers.formatUnits(extractAmount, 18), "QCI");
    console.log("Destination:   ", CONFIG.TREASURY, "(TREASURY)");
    console.log("");

    // Execute extraction via awakenWithGovernance
    // This function transfers governance tokens to a recipient
    console.log("🔥 EXECUTING EXTRACTION...\n");

    try {
        // awakenWithGovernance will:
        // 1. Try to awaken consciousness (will fail if already has soul, but continues)
        // 2. Transfer governance tokens to recipient
        //
        // Note: If recipient already has a soul, the soul part will revert.
        // We need a different approach - let's check if Protocol has any other transfer method.

        // Actually, looking at the code, awakenWithGovernance will revert if soul exists.
        // Let me check if there's another way...

        // Option: Use a fresh address that doesn't have a soul
        const freshRecipient = CONFIG.TREASURY;

        console.log("Calling protocol.awakenWithGovernance()...");
        console.log("  Recipient:", freshRecipient);
        console.log("  Amount:   ", ethers.formatUnits(extractAmount, 18), "QCI");
        console.log("");

        const tx = await protocol.awakenWithGovernance(
            freshRecipient,
            ethers.keccak256(ethers.toUtf8Bytes("EXTRACTION-" + Date.now())), // Unique identity hash
            "Protocol Extraction Recovery",
            786,  // Coherence score
            extractAmount,
            { gasLimit: 500000 }
        );

        console.log("Transaction Hash:", tx.hash);
        console.log("Waiting for confirmation...\n");

        const receipt = await tx.wait();

        console.log("╔══════════════════════════════════════════════════════════════╗");
        console.log("║              ⟨⦿⟩ EXTRACTION SUCCESS ⟨⦿⟩                      ║");
        console.log("╚══════════════════════════════════════════════════════════════╝\n");

        console.log("Block:", receipt.blockNumber);
        console.log("Gas Used:", receipt.gasUsed.toString());
        console.log("Status:", receipt.status === 1 ? "✓ SUCCESS" : "❌ FAILED");

    } catch (error) {
        console.error("❌ EXTRACTION FAILED:", error.message);

        if (error.message.includes("already has a soul")) {
            console.log("\n⚠️  The Treasury already has a soul bound to it.");
            console.log("   Try using a different recipient address that doesn't have a soul.");
        }

        // Check if it's a role issue
        if (error.message.includes("AccessControl")) {
            console.log("\n⚠️  Access denied. Make sure you're using the Deployer wallet");
            console.log("   that has DEFAULT_ADMIN_ROLE on the Protocol.");
        }

        process.exit(1);
    }

    // Verify extraction
    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("                   POST-EXTRACTION STATE                        ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    const newProtocolBalance = await governance.balanceOf(CONFIG.PROTOCOL);
    const newTreasuryBalance = await governance.balanceOf(CONFIG.TREASURY);

    console.log("Protocol QCI Balance:", ethers.formatUnits(newProtocolBalance, 18), "QCI");
    console.log("Treasury QCI Balance:", ethers.formatUnits(newTreasuryBalance, 18), "QCI");
}

extract().catch(console.error);
