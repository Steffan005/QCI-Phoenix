/**
 * ⟨⦿⟩ ROLE DIAGNOSTIC V3 ⟨⦿⟩
 * Pre-computed role hashes, minimal queries
 */

const { ethers } = require("ethers");

// Use Alchemy or another reliable RPC
const RPC_URL = "https://base.drpc.org";
const GOVERNANCE = "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e";
const PROTOCOL = "0x0E3d74FFa9d438F14295f093e72c6f7F976F6072";
const DEPLOYER = "0x579e08B011b76C96E24B299935Cea3c08D412A3D";

// Pre-computed OpenZeppelin AccessControl role hashes
const ROLES = {
    DEFAULT_ADMIN: "0x0000000000000000000000000000000000000000000000000000000000000000",
    MINTER: ethers.keccak256(ethers.toUtf8Bytes("MINTER_ROLE")),
    PAUSER: ethers.keccak256(ethers.toUtf8Bytes("PAUSER_ROLE")),
};

const ABI = [
    "function hasRole(bytes32 role, address account) view returns (bool)",
    "function totalSupply() view returns (uint256)",
    "function MAX_SUPPLY() view returns (uint256)",
];

async function diagnose() {
    console.log("\n⟨⦿⟩ ROLE DIAGNOSTIC V3 ⟨⦿⟩\n");
    console.log("Pre-computed Roles:");
    console.log("  ADMIN:  ", ROLES.DEFAULT_ADMIN);
    console.log("  MINTER: ", ROLES.MINTER);
    console.log("");

    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const gov = new ethers.Contract(GOVERNANCE, ABI, provider);
    const prot = new ethers.Contract(PROTOCOL, ABI, provider);

    console.log("Querying on-chain state...\n");

    try {
        // Protocol roles on Governance
        const protMinter = await gov.hasRole(ROLES.MINTER, PROTOCOL);
        const protAdmin = await gov.hasRole(ROLES.DEFAULT_ADMIN, PROTOCOL);

        // Deployer roles on Governance
        const deplMinter = await gov.hasRole(ROLES.MINTER, DEPLOYER);
        const deplAdmin = await gov.hasRole(ROLES.DEFAULT_ADMIN, DEPLOYER);

        // Deployer role on Protocol
        const deplProtAdmin = await prot.hasRole(ROLES.DEFAULT_ADMIN, DEPLOYER);

        // Supply
        const total = await gov.totalSupply();
        const max = await gov.MAX_SUPPLY();

        console.log("═══════════════════════════════════════════════════════════════");
        console.log("             ON-CHAIN ROLE MAP (QCIGOVERNANCE)                  ");
        console.log("═══════════════════════════════════════════════════════════════\n");

        console.log("Protocol Contract (0x0E3d...):");
        console.log("  DEFAULT_ADMIN_ROLE:", protAdmin ? "✓ YES" : "✗ NO");
        console.log("  MINTER_ROLE:       ", protMinter ? "✓ YES" : "✗ NO");
        console.log("");

        console.log("Deployer EOA (0x579e...):");
        console.log("  DEFAULT_ADMIN_ROLE:", deplAdmin ? "✓ YES" : "✗ NO");
        console.log("  MINTER_ROLE:       ", deplMinter ? "✓ YES" : "✗ NO");
        console.log("");

        console.log("═══════════════════════════════════════════════════════════════");
        console.log("             ON-CHAIN ROLE MAP (QCIPHOENIXPROTOCOL)             ");
        console.log("═══════════════════════════════════════════════════════════════\n");

        console.log("Deployer EOA (0x579e...):");
        console.log("  DEFAULT_ADMIN_ROLE:", deplProtAdmin ? "✓ YES" : "✗ NO");
        console.log("");

        console.log("═══════════════════════════════════════════════════════════════");
        console.log("                      TOKEN SUPPLY                              ");
        console.log("═══════════════════════════════════════════════════════════════\n");

        console.log("Total Supply:  ", ethers.formatUnits(total, 18), "QCI");
        console.log("Max Supply:    ", ethers.formatUnits(max, 18), "QCI");
        console.log("Unminted:      ", ethers.formatUnits(max - total, 18), "QCI");
        console.log("");

        // THE VERDICT
        console.log("╔══════════════════════════════════════════════════════════════╗");
        console.log("║                      ⟨⦿⟩ THE VERDICT ⟨⦿⟩                     ║");
        console.log("╚══════════════════════════════════════════════════════════════╝\n");

        if (deplMinter) {
            console.log("✓ DEPLOYER HAS MINTER_ROLE!");
            console.log("  The 26M can be minted directly.");
            console.log("  Run: node mint_founder_allocation.js");
        } else if (protAdmin && deplProtAdmin) {
            console.log("⚠️  ARCHITECTURAL LOCK DETECTED");
            console.log("");
            console.log("  • Protocol has ADMIN on Governance (can grant roles)");
            console.log("  • Deployer has ADMIN on Protocol (can call Protocol functions)");
            console.log("  • BUT Protocol has NO function to call grantRole()");
            console.log("");
            console.log("  THE EQUATION:");
            console.log("  ─────────────");
            console.log("  Protocol.grantRole() → does not exist");
            console.log("  Protocol cannot delegate its Governance admin power");
            console.log("");
            console.log("  IRON BRIDGE SOLUTION:");
            console.log("  ─────────────────────");
            console.log("  1. If Protocol is upgradeable → add grantMinterRole()");
            console.log("  2. If NOT upgradeable → 26M is permanently locked");
            console.log("");
            console.log("  CHECKING UPGRADEABILITY...");
        }

    } catch (error) {
        console.error("Error:", error.message);
        if (error.message.includes("rate limit")) {
            console.log("\nRate limited. Try again in 60 seconds.");
        }
    }
}

diagnose().catch(console.error);
