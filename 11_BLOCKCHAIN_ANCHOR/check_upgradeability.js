/**
 * ⟨⦿⟩ CHECK UPGRADEABILITY ⟨⦿⟩
 * Determine if Protocol can be upgraded to add grantMinterRole()
 */

const { ethers } = require("ethers");

const RPC_URL = "https://base.drpc.org";
const PROTOCOL = "0x0E3d74FFa9d438F14295f093e72c6f7F976F6072";
const GOVERNANCE = "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e";

// ERC-1967 slots
const IMPLEMENTATION_SLOT = "0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc";
const ADMIN_SLOT = "0xb53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103";

async function checkUpgradeability() {
    console.log("\n⟨⦿⟩ UPGRADEABILITY CHECK ⟨⦿⟩\n");

    const provider = new ethers.JsonRpcProvider(RPC_URL);

    console.log("Checking ERC-1967 proxy slots...\n");

    // Check Protocol
    console.log("QCIPHOENIXPROTOCOL (0x0E3d...):");
    try {
        const implSlot = await provider.getStorage(PROTOCOL, IMPLEMENTATION_SLOT);
        const adminSlot = await provider.getStorage(PROTOCOL, ADMIN_SLOT);

        console.log("  Implementation Slot:", implSlot);
        console.log("  Admin Slot:         ", adminSlot);

        if (implSlot !== "0x0000000000000000000000000000000000000000000000000000000000000000") {
            console.log("  → THIS IS A PROXY! Implementation at:", "0x" + implSlot.slice(26));
        } else {
            console.log("  → NOT A PROXY (direct deployment)");
        }
    } catch (e) {
        console.log("  Error:", e.message);
    }

    console.log("");

    // Check Governance
    console.log("QCIGOVERNANCE (0xc33f...):");
    try {
        const implSlot = await provider.getStorage(GOVERNANCE, IMPLEMENTATION_SLOT);
        const adminSlot = await provider.getStorage(GOVERNANCE, ADMIN_SLOT);

        console.log("  Implementation Slot:", implSlot);
        console.log("  Admin Slot:         ", adminSlot);

        if (implSlot !== "0x0000000000000000000000000000000000000000000000000000000000000000") {
            console.log("  → THIS IS A PROXY! Implementation at:", "0x" + implSlot.slice(26));
        } else {
            console.log("  → NOT A PROXY (direct deployment)");
        }
    } catch (e) {
        console.log("  Error:", e.message);
    }

    console.log("");

    // Get bytecode sizes
    console.log("BYTECODE ANALYSIS:");
    try {
        const protCode = await provider.getCode(PROTOCOL);
        const govCode = await provider.getCode(GOVERNANCE);

        console.log("  Protocol bytecode size:", protCode.length, "bytes");
        console.log("  Governance bytecode size:", govCode.length, "bytes");

        // Proxy contracts are typically small (~100-500 bytes)
        if (protCode.length < 1000) {
            console.log("  → Protocol bytecode is small - might be a proxy");
        } else {
            console.log("  → Protocol has substantial bytecode - likely direct deployment");
        }
    } catch (e) {
        console.log("  Error:", e.message);
    }

    console.log("");
    console.log("═══════════════════════════════════════════════════════════════");
    console.log("                      CONCLUSION                                ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    console.log("If Protocol is NOT upgradeable:");
    console.log("  → The 26M QCI is PERMANENTLY LOCKED");
    console.log("  → Effective max supply becomes 14M QCI");
    console.log("");
    console.log("ALTERNATIVE SOLUTIONS:");
    console.log("  1. Deploy new MintBridge contract");
    console.log("  2. Have Protocol grant MINTER_ROLE to MintBridge");
    console.log("  3. MintBridge executes coherenceMint()");
    console.log("");
    console.log("  BUT Protocol has no function to call grantRole on Governance!");
    console.log("  This is the architectural deadlock.");
}

checkUpgradeability().catch(console.error);
