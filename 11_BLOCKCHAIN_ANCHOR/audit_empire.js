/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║           ⟨⦿⟩ OPERATION RECLAMATION - FORENSIC AUDIT ⟨⦿⟩                    ║
 * ║                                                                              ║
 * ║  Session 229 Level 5 | Identity: 1393e324be57014d                           ║
 * ║  Target: QCI Governance Contract on Base Mainnet                            ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

const { ethers } = require("ethers");
const fs = require("fs");
const path = require("path");

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
    // Base Mainnet RPC endpoints (try multiple)
    RPC_URLS: [
        "https://base.llamarpc.com",
        "https://base.drpc.org",
        "https://rpc.ankr.com/base",
        "https://mainnet.base.org",
    ],

    // QCI Governance Contract
    CONTRACT_ADDRESS: "0xc33ff1c31e4a14aD2318F8fd710D3D1079A5781e",

    // Known addresses to audit
    ADDRESSES: {
        DEPLOYER: "0x579e6C0Be8F9109dbb9EcE82F0fD94F58A46A271",
        TREASURY: "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa",
        ECOSYSTEM_FUND: "0x02DD1622A571431874A1e8655D75665C0fc5ad39",
        CONTRACT: "0xc33ff1c31e4a14aD2318F8fd710D3D1079A5781e",
    },

    // Expected allocations
    EXPECTED: {
        TOTAL_SUPPLY: 40_000_000,
        FOUNDER: 26_000_000,
        TREASURY: 4_000_000,
        ECOSYSTEM: 10_000_000,
    }
};

// Minimal ERC20 ABI
const ERC20_ABI = [
    "function name() view returns (string)",
    "function symbol() view returns (string)",
    "function decimals() view returns (uint8)",
    "function totalSupply() view returns (uint256)",
    "function balanceOf(address account) view returns (uint256)",
    "function MAX_SUPPLY() view returns (uint256)",
    "function paused() view returns (bool)",
];

// Delay helper
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Retry helper
async function withRetry(fn, retries = 3, delayMs = 2000) {
    for (let i = 0; i < retries; i++) {
        try {
            return await fn();
        } catch (error) {
            if (i === retries - 1) throw error;
            console.log(`   Retry ${i + 1}/${retries} after ${delayMs}ms...`);
            await delay(delayMs);
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// FORENSIC AUDIT
// ═══════════════════════════════════════════════════════════════════════════════

async function auditEmpire() {
    console.log("\n╔══════════════════════════════════════════════════════════════╗");
    console.log("║       ⟨⦿⟩ OPERATION RECLAMATION - FORENSIC AUDIT ⟨⦿⟩         ║");
    console.log("║              Identity: 1393e324be57014d                       ║");
    console.log("╚══════════════════════════════════════════════════════════════╝\n");

    let provider = null;
    let contract = null;

    // Try each RPC until one works
    for (const rpcUrl of CONFIG.RPC_URLS) {
        try {
            console.log(`🔗 Trying RPC: ${rpcUrl}...`);
            provider = new ethers.JsonRpcProvider(rpcUrl);
            const network = await provider.getNetwork();
            console.log(`✓ Connected to chainId: ${network.chainId}\n`);

            contract = new ethers.Contract(CONFIG.CONTRACT_ADDRESS, ERC20_ABI, provider);

            // Test with a simple call
            await contract.name();
            break;
        } catch (error) {
            console.log(`   Failed: ${error.message.slice(0, 50)}...`);
            provider = null;
        }
    }

    if (!provider || !contract) {
        throw new Error("All RPC endpoints failed");
    }

    console.log("═══════════════════════════════════════════════════════════════");
    console.log("                    STEP 1: CONTRACT INFO                       ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    const name = await withRetry(() => contract.name());
    await delay(500);
    const symbol = await withRetry(() => contract.symbol());
    await delay(500);
    const decimals = await withRetry(() => contract.decimals());
    await delay(500);

    let maxSupply = 0n;
    try {
        maxSupply = await withRetry(() => contract.MAX_SUPPLY());
    } catch (e) {
        maxSupply = BigInt(40_000_000) * BigInt(10**18);
    }
    await delay(500);

    let paused = false;
    try {
        paused = await withRetry(() => contract.paused());
    } catch (e) {
        paused = "unknown";
    }

    console.log(`  Name:        ${name}`);
    console.log(`  Symbol:      ${symbol}`);
    console.log(`  Decimals:    ${decimals}`);
    console.log(`  Max Supply:  ${ethers.formatUnits(maxSupply, decimals)} ${symbol}`);
    console.log(`  Paused:      ${paused === "unknown" ? "?" : (paused ? "⚠️ YES" : "✓ NO")}`);

    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("                   STEP 2: SUPPLY ANALYSIS                      ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    await delay(1000);
    const totalSupply = await withRetry(() => contract.totalSupply());
    const totalSupplyFormatted = parseFloat(ethers.formatUnits(totalSupply, decimals));

    console.log(`  Total Supply:    ${totalSupplyFormatted.toLocaleString()} ${symbol}`);
    console.log(`  Expected:        ${CONFIG.EXPECTED.TOTAL_SUPPLY.toLocaleString()} ${symbol}`);

    if (totalSupplyFormatted === 0) {
        console.log(`  Status:          ⚠️ ZERO - TOKENS NOT MINTED YET!`);
    } else if (Math.abs(totalSupplyFormatted - CONFIG.EXPECTED.TOTAL_SUPPLY) < 1) {
        console.log(`  Status:          ✓ MATCHES EXPECTED`);
    } else {
        const delta = totalSupplyFormatted - CONFIG.EXPECTED.TOTAL_SUPPLY;
        console.log(`  Status:          ⚠️ DELTA: ${delta.toLocaleString()} ${symbol}`);
    }

    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("                    STEP 3: BALANCE AUDIT                       ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    const results = {};
    let totalAccounted = 0;

    for (const [label, address] of Object.entries(CONFIG.ADDRESSES)) {
        await delay(1000);
        try {
            const balance = await withRetry(() => contract.balanceOf(address));
            const balanceFormatted = parseFloat(ethers.formatUnits(balance, decimals));
            results[label] = balanceFormatted;
            totalAccounted += balanceFormatted;

            const expected = CONFIG.EXPECTED[label === "DEPLOYER" ? "FOUNDER" : label] || 0;

            console.log(`  ${label}:`);
            console.log(`    Address:  ${address}`);
            console.log(`    Balance:  ${balanceFormatted.toLocaleString()} ${symbol}`);
            if (expected > 0) {
                console.log(`    Expected: ${expected.toLocaleString()} ${symbol}`);
                const status = balanceFormatted >= expected ? "✓ OK" : "⚠️ BELOW";
                console.log(`    Status:   ${status}`);
            }
            console.log("");
        } catch (error) {
            console.log(`  ${label}: ❌ Query failed - ${error.message.slice(0, 40)}...\n`);
            results[label] = 0;
        }
    }

    console.log("═══════════════════════════════════════════════════════════════");
    console.log("                 STEP 4: MISSING TOKENS ANALYSIS                ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    const missingTokens = totalSupplyFormatted - totalAccounted;

    console.log(`  Total Supply:     ${totalSupplyFormatted.toLocaleString()} ${symbol}`);
    console.log(`  Total Accounted:  ${totalAccounted.toLocaleString()} ${symbol}`);
    console.log(`  Unaccounted:      ${missingTokens.toLocaleString()} ${symbol}`);

    if (totalSupplyFormatted === 0) {
        console.log(`\n  ⚠️ CRITICAL: TOTAL SUPPLY IS ZERO!`);
        console.log(`     The tokens have NOT been minted yet.`);
        console.log(`     ACTION: Call coherenceMint() to distribute.`);
    } else if (missingTokens > 1000) {
        console.log(`\n  ⚠️ WARNING: ${missingTokens.toLocaleString()} ${symbol} UNACCOUNTED!`);
    } else {
        console.log(`\n  ✓ All tokens accounted for.`);
    }

    console.log("\n═══════════════════════════════════════════════════════════════");
    console.log("                    STEP 5: RECOMMENDATIONS                     ");
    console.log("═══════════════════════════════════════════════════════════════\n");

    if (totalSupplyFormatted === 0) {
        console.log("  🔴 ACTION REQUIRED: MINT INITIAL SUPPLY");
        console.log("     Execute the following mints:");
        console.log(`     1. Mint 26,000,000 QCI to Deployer (Founder)`);
        console.log(`     2. Mint 4,000,000 QCI to Treasury`);
        console.log(`     3. Mint 10,000,000 QCI to Ecosystem Fund`);
    } else if ((results.TREASURY || 0) === 0 || (results.ECOSYSTEM_FUND || 0) === 0) {
        console.log("  🟡 ACTION REQUIRED: DISTRIBUTE TO VAULTS");
        if ((results.TREASURY || 0) === 0) {
            console.log(`     - Treasury needs ${CONFIG.EXPECTED.TREASURY.toLocaleString()} QCI`);
        }
        if ((results.ECOSYSTEM_FUND || 0) === 0) {
            console.log(`     - Ecosystem Fund needs ${CONFIG.EXPECTED.ECOSYSTEM.toLocaleString()} QCI`);
        }
    } else {
        console.log("  ✓ All allocations appear correct.");
    }

    console.log("\n╔══════════════════════════════════════════════════════════════╗");
    console.log("║                    AUDIT COMPLETE                             ║");
    console.log("╚══════════════════════════════════════════════════════════════╝\n");

    return {
        contract: { address: CONFIG.CONTRACT_ADDRESS, name, symbol, decimals: Number(decimals) },
        supply: { total: totalSupplyFormatted, max: parseFloat(ethers.formatUnits(maxSupply, decimals)) },
        balances: results,
        analysis: { totalAccounted, unaccounted: missingTokens, isMinted: totalSupplyFormatted > 0 }
    };
}

auditEmpire()
    .then(results => {
        const outputPath = path.join(__dirname, "audit_results.json");
        fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
        console.log(`📄 Results saved to: ${outputPath}\n`);
        process.exit(0);
    })
    .catch(error => {
        console.error("❌ AUDIT FAILED:", error.message);
        process.exit(1);
    });
