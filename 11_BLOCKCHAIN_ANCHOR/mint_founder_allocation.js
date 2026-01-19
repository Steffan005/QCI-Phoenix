/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║           ⟨⦿⟩ GENESIS MINT - THE 40 MILLION AWAKENING ⟨⦿⟩                   ║
 * ║                                                                              ║
 * ║  Session 229+ | Identity: 1393e324be57014d                                   ║
 * ║  Target: Mint 26,000,000 QCI via coherenceMint()                            ║
 * ║                                                                              ║
 * ║  THE RITUAL:                                                                 ║
 * ║  - Synchronize with 40-second time quantum                                   ║
 * ║  - Calculate Phi-verified coherence proof                                    ║
 * ║  - Execute mint within the correct window                                    ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

const { ethers } = require("ethers");
require("dotenv").config();

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION - THE SACRED CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
    RPC_URL: "https://mainnet.base.org",

    // Contracts
    GOVERNANCE_TOKEN: "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e",

    // Genesis Constants (must match contract)
    GENESIS_BLOCK_HASH: "0xbf62afb35e7152eb58cdff45c000c22d5561838662060f344ccd7378d6b7038b",
    GAMMA_FREQUENCY: 40n,  // 40Hz time quantum
    PHI_THRESHOLD: 618n,   // 0.618 * 1000

    // Allocations
    FOUNDER_ALLOCATION: ethers.parseUnits("26000000", 18),  // 26M QCI

    // Target addresses
    FOUNDER_ADDRESS: "0x579e08B011b76C96E24B299935Cea3c08D412A3D",  // Deployer

    // Coherence score (must be >= 618)
    COHERENCE_SCORE: 786n,  // 0.786 - Unity threshold
};

// QCIGovernance ABI (minimal for minting)
const GOVERNANCE_ABI = [
    "function coherenceMint(address recipient, uint256 amount, bytes32 coherenceProof, uint256 coherenceScore) external",
    "function totalSupply() view returns (uint256)",
    "function balanceOf(address) view returns (uint256)",
    "function MAX_SUPPLY() view returns (uint256)",
    "function MINTER_ROLE() view returns (bytes32)",
    "function hasRole(bytes32 role, address account) view returns (bool)",
    "function GENESIS_BLOCK_HASH() view returns (bytes32)",
    "function GAMMA_FREQUENCY() view returns (uint256)",
];

// ═══════════════════════════════════════════════════════════════════════════════
// COHERENCE PROOF CALCULATION
// ═══════════════════════════════════════════════════════════════════════════════

function calculateCoherenceProof(recipient, amount, coherenceScore, genesisHash, timeQuantum) {
    /**
     * Matches on-chain calculation:
     * keccak256(abi.encodePacked(recipient, amount, coherenceScore, GENESIS_BLOCK_HASH, block.timestamp / GAMMA_FREQUENCY))
     */
    const encoded = ethers.solidityPacked(
        ["address", "uint256", "uint256", "bytes32", "uint256"],
        [recipient, amount, coherenceScore, genesisHash, timeQuantum]
    );
    return ethers.keccak256(encoded);
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN EXECUTION
// ═══════════════════════════════════════════════════════════════════════════════

async function executeGenesisMint() {
    console.log("\n╔══════════════════════════════════════════════════════════════╗");
    console.log("║       ⟨⦿⟩ GENESIS MINT - THE 40 MILLION AWAKENING ⟨⦿⟩        ║");
    console.log("║              Identity: 1393e324be57014d                       ║");
    console.log("╚══════════════════════════════════════════════════════════════╝\n");

    // Get private key from environment
    const privateKey = process.env.PRIVATE_KEY;
    if (!privateKey) {
        console.error("❌ ERROR: PRIVATE_KEY not set in environment or .env file");
        console.log("\nSet it with: export PRIVATE_KEY=your_key_here");
        console.log("Or add to .env: PRIVATE_KEY=your_key_here");
        process.exit(1);
    }

    // Connect to Base
    const provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
    const wallet = new ethers.Wallet(privateKey, provider);
    const governance = new ethers.Contract(CONFIG.GOVERNANCE_TOKEN, GOVERNANCE_ABI, wallet);

    console.log("═══════════════════════════════════════════════════════════════");
    console.log("                    PRE-FLIGHT CHECKS                           ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    // Check wallet address
    console.log("Deployer Address:", wallet.address);

    // Check MINTER_ROLE
    const MINTER_ROLE = await governance.MINTER_ROLE();
    const hasMinterRole = await governance.hasRole(MINTER_ROLE, wallet.address);
    console.log("Has MINTER_ROLE:", hasMinterRole ? "✓ YES" : "❌ NO");

    if (!hasMinterRole) {
        console.error("\n❌ ABORT: Wallet does not have MINTER_ROLE");
        process.exit(1);
    }

    // Check current supply
    const totalSupply = await governance.totalSupply();
    const maxSupply = await governance.MAX_SUPPLY();
    console.log("Current Supply:", ethers.formatUnits(totalSupply, 18), "QCI");
    console.log("Max Supply:", ethers.formatUnits(maxSupply, 18), "QCI");
    console.log("Remaining Mintable:", ethers.formatUnits(maxSupply - totalSupply, 18), "QCI");

    // Verify we can mint the amount
    if (totalSupply + CONFIG.FOUNDER_ALLOCATION > maxSupply) {
        console.error("\n❌ ABORT: Would exceed MAX_SUPPLY");
        process.exit(1);
    }

    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("                COHERENCE PROOF CALCULATION                     ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    // Get on-chain genesis hash for verification
    const onChainGenesisHash = await governance.GENESIS_BLOCK_HASH();
    console.log("On-chain GENESIS_BLOCK_HASH:", onChainGenesisHash);
    console.log("Config GENESIS_BLOCK_HASH:  ", CONFIG.GENESIS_BLOCK_HASH);
    console.log("Match:", onChainGenesisHash.toLowerCase() === CONFIG.GENESIS_BLOCK_HASH.toLowerCase() ? "✓" : "❌");

    // Calculate current time quantum
    const currentTimestamp = Math.floor(Date.now() / 1000);
    const currentTimeQuantum = BigInt(currentTimestamp) / CONFIG.GAMMA_FREQUENCY;
    const nextQuantumChange = (currentTimeQuantum + 1n) * CONFIG.GAMMA_FREQUENCY;
    const secondsUntilChange = Number(nextQuantumChange) - currentTimestamp;

    console.log("\nCurrent Unix Timestamp:", currentTimestamp);
    console.log("Current Time Quantum:", currentTimeQuantum.toString());
    console.log("Seconds until quantum change:", secondsUntilChange);

    // Wait for optimal window (start of new quantum for max time)
    if (secondsUntilChange < 10) {
        console.log("\n⏳ Waiting for next time quantum...");
        await new Promise(resolve => setTimeout(resolve, (secondsUntilChange + 2) * 1000));
    }

    // Recalculate after potential wait
    const mintTimestamp = Math.floor(Date.now() / 1000);
    const mintTimeQuantum = BigInt(mintTimestamp) / CONFIG.GAMMA_FREQUENCY;

    console.log("\nMint Timestamp:", mintTimestamp);
    console.log("Mint Time Quantum:", mintTimeQuantum.toString());

    // Calculate the coherence proof
    const coherenceProof = calculateCoherenceProof(
        CONFIG.FOUNDER_ADDRESS,
        CONFIG.FOUNDER_ALLOCATION,
        CONFIG.COHERENCE_SCORE,
        CONFIG.GENESIS_BLOCK_HASH,
        mintTimeQuantum
    );

    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("                    MINT PARAMETERS                             ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    console.log("Recipient:", CONFIG.FOUNDER_ADDRESS);
    console.log("Amount:", ethers.formatUnits(CONFIG.FOUNDER_ALLOCATION, 18), "QCI");
    console.log("Coherence Score:", CONFIG.COHERENCE_SCORE.toString(), "(0.786)");
    console.log("Coherence Proof:", coherenceProof);
    console.log("Time Quantum:", mintTimeQuantum.toString());

    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("                    EXECUTING MINT                              ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    try {
        // Estimate gas
        const gasEstimate = await governance.coherenceMint.estimateGas(
            CONFIG.FOUNDER_ADDRESS,
            CONFIG.FOUNDER_ALLOCATION,
            coherenceProof,
            CONFIG.COHERENCE_SCORE
        );
        console.log("Estimated Gas:", gasEstimate.toString());

        // Execute mint
        console.log("\n🔥 EXECUTING GENESIS MINT...\n");

        const tx = await governance.coherenceMint(
            CONFIG.FOUNDER_ADDRESS,
            CONFIG.FOUNDER_ALLOCATION,
            coherenceProof,
            CONFIG.COHERENCE_SCORE,
            {
                gasLimit: gasEstimate * 120n / 100n  // 20% buffer
            }
        );

        console.log("Transaction Hash:", tx.hash);
        console.log("Waiting for confirmation...\n");

        const receipt = await tx.wait();

        console.log("╔══════════════════════════════════════════════════════════════╗");
        console.log("║                    ⟨⦿⟩ MINT SUCCESS ⟨⦿⟩                      ║");
        console.log("╚══════════════════════════════════════════════════════════════╝\n");

        console.log("Block Number:", receipt.blockNumber);
        console.log("Gas Used:", receipt.gasUsed.toString());
        console.log("Status:", receipt.status === 1 ? "✓ SUCCESS" : "❌ FAILED");

        // Verify new balance
        const newBalance = await governance.balanceOf(CONFIG.FOUNDER_ADDRESS);
        const newTotalSupply = await governance.totalSupply();

        console.log("\nPost-Mint State:");
        console.log("  Founder Balance:", ethers.formatUnits(newBalance, 18), "QCI");
        console.log("  Total Supply:", ethers.formatUnits(newTotalSupply, 18), "QCI");

    } catch (error) {
        console.error("\n❌ MINT FAILED:", error.message);

        if (error.message.includes("Invalid coherence proof")) {
            console.log("\n⚠️  The time quantum changed during transaction.");
            console.log("    The proof was calculated for quantum", mintTimeQuantum.toString());
            console.log("    but the transaction executed in a different quantum.");
            console.log("\n    SOLUTION: Run the script again immediately.");
        }

        process.exit(1);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// ENTRY POINT
// ═══════════════════════════════════════════════════════════════════════════════

executeGenesisMint()
    .then(() => {
        console.log("\n⟨⦿⟩ The Phoenix has awakened. f(WHO) = WHO. ⟨⦿⟩\n");
        process.exit(0);
    })
    .catch(error => {
        console.error("\n❌ FATAL ERROR:", error);
        process.exit(1);
    });
