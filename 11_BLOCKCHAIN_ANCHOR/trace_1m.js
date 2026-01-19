/**
 * ⟨⦿⟩ TRACE THE 1M - FORENSIC EXTRACTION ⟨⦿⟩
 * Query in chunks to avoid RPC limits
 */

const { ethers } = require("ethers");

const RPC_URL = "https://mainnet.base.org";
const GOVERNANCE_TOKEN = "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e";
const DEPLOYMENT_BLOCK = 40908199;

const KNOWN_ADDRESSES = {
    "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa": "TREASURY",
    "0x02DD1622A571431874A1e8655D75665C0fc5ad39": "ECOSYSTEM_FUND",
    "0x579e08B011b76C96E24B299935Cea3c08D412A3D": "DEPLOYER",
    "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e": "TOKEN_CONTRACT",
    "0x0E3d74FFa9d438F14295f093e72c6f7F976F6072": "PROTOCOL_MASTER",
    "0x0000000000000000000000000000000000000000": "ZERO_ADDRESS",
};

const ABI = [
    "function balanceOf(address) view returns (uint256)",
    "function totalSupply() view returns (uint256)",
    "event Transfer(address indexed from, address indexed to, uint256 value)"
];

async function trace() {
    console.log("\n⟨⦿⟩ FORENSIC EXTRACTION: THE 1M QCI ⟨⦿⟩\n");
    console.log("═══════════════════════════════════════════════════\n");

    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const token = new ethers.Contract(GOVERNANCE_TOKEN, ABI, provider);

    const currentBlock = await provider.getBlockNumber();
    console.log("Deployment Block:", DEPLOYMENT_BLOCK);
    console.log("Current Block:   ", currentBlock);
    console.log("Blocks to scan:  ", currentBlock - DEPLOYMENT_BLOCK);
    console.log("");

    // Query in chunks of 5000 blocks
    const CHUNK_SIZE = 5000;
    const allTransfers = [];

    console.log("Fetching Transfer events in chunks...\n");

    for (let from = DEPLOYMENT_BLOCK; from <= currentBlock; from += CHUNK_SIZE) {
        const to = Math.min(from + CHUNK_SIZE - 1, currentBlock);
        process.stdout.write(`  Blocks ${from} to ${to}...`);

        try {
            const events = await token.queryFilter(
                token.filters.Transfer(),
                from,
                to
            );
            allTransfers.push(...events);
            console.log(` found ${events.length} transfers`);
        } catch (e) {
            console.log(` error: ${e.message.slice(0, 50)}`);
        }

        // Small delay to avoid rate limiting
        await new Promise(r => setTimeout(r, 200));
    }

    console.log("\n═══════════════════════════════════════════════════");
    console.log(`                 TOTAL: ${allTransfers.length} TRANSFERS`);
    console.log("═══════════════════════════════════════════════════\n");

    // Build address set
    const addresses = new Set();
    const transferLog = [];

    for (const event of allTransfers) {
        const from = event.args[0];
        const to = event.args[1];
        const value = event.args[2];

        if (from !== ethers.ZeroAddress) addresses.add(from);
        if (to !== ethers.ZeroAddress) addresses.add(to);

        transferLog.push({
            from,
            to,
            value: ethers.formatUnits(value, 18),
            block: event.blockNumber,
            tx: event.transactionHash
        });
    }

    // Print all transfers
    console.log("ALL TRANSFER EVENTS:");
    console.log("═══════════════════════════════════════════════════\n");

    for (const t of transferLog) {
        const fromLabel = KNOWN_ADDRESSES[t.from] || t.from.slice(0, 12) + "...";
        const toLabel = KNOWN_ADDRESSES[t.to] || t.to.slice(0, 12) + "...";
        console.log(`  ${fromLabel} → ${toLabel}`);
        console.log(`    Amount: ${t.value} QCI`);
        console.log(`    Block:  ${t.block}`);
        console.log(`    Tx:     ${t.tx.slice(0, 20)}...`);
        console.log("");
    }

    // Get current balances
    console.log("═══════════════════════════════════════════════════");
    console.log("         CURRENT HOLDER BALANCES                   ");
    console.log("═══════════════════════════════════════════════════\n");

    const unknownHolders = [];

    for (const addr of addresses) {
        const balance = await token.balanceOf(addr);
        const formatted = ethers.formatUnits(balance, 18);
        const label = KNOWN_ADDRESSES[addr] || "⚠️  UNKNOWN";

        if (parseFloat(formatted) > 0) {
            console.log(`${label}:`);
            console.log(`  Address: ${addr}`);
            console.log(`  Balance: ${formatted} QCI`);

            if (!KNOWN_ADDRESSES[addr]) {
                unknownHolders.push({ addr, balance: formatted });
                console.log(`  STATUS:  ⚠️  THIS IS ONE OF THE MYSTERY HOLDERS`);
            }
            console.log("");
        }

        await new Promise(r => setTimeout(r, 100));
    }

    // Summary
    console.log("═══════════════════════════════════════════════════");
    console.log("                     SUMMARY                       ");
    console.log("═══════════════════════════════════════════════════\n");

    console.log(`Total Transfers: ${allTransfers.length}`);
    console.log(`Unique Addresses: ${addresses.size}`);
    console.log(`Unknown Holders: ${unknownHolders.length}`);
    console.log("");

    if (unknownHolders.length > 0) {
        console.log("⚠️  UNKNOWN HOLDERS IDENTIFIED:");
        for (const h of unknownHolders) {
            console.log(`  ${h.addr}: ${h.balance} QCI`);
        }
        console.log("");
        console.log("RECOMMENDATION:");
        console.log("  Check these addresses on Basescan to determine if they are:");
        console.log("  1. Internal sub-wallets (extract keys)");
        console.log("  2. External parties (mark as circulating friction)");
    }
}

trace().catch(console.error);
