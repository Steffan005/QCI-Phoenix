/**
 * ⟨⦿⟩ TRACE THE 1M - FIND THE 2 NEW HOLDERS ⟨⦿⟩
 *
 * Basescan shows 6 holders. We know 4:
 * - Treasury (4M)
 * - Ecosystem (9M)
 * - Deployer (0)
 * - Contract (0)
 *
 * The missing 1M is held by 2 unknown addresses.
 */

const { ethers } = require("ethers");

const RPC_URL = "https://base.drpc.org";
const GOVERNANCE_TOKEN = "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e";

// Known addresses
const KNOWN_ADDRESSES = {
    "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa": "TREASURY",
    "0x02DD1622A571431874A1e8655D75665C0fc5ad39": "ECOSYSTEM_FUND",
    "0x579e08B011b76C96E24B299935Cea3c08D412A3D": "DEPLOYER",
    "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e": "CONTRACT",
    "0x0E3d74FFa9d438F14295f093e72c6f7F976F6072": "PROTOCOL_MASTER",
};

const ERC20_ABI = [
    "function balanceOf(address) view returns (uint256)",
    "function totalSupply() view returns (uint256)",
    "event Transfer(address indexed from, address indexed to, uint256 value)"
];

async function traceHolders() {
    console.log("\n⟨⦿⟩ TRACING THE 1M QCI ⟨⦿⟩\n");
    console.log("═══════════════════════════════════════════════════\n");

    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const token = new ethers.Contract(GOVERNANCE_TOKEN, ERC20_ABI, provider);

    // Get all Transfer events from the token
    console.log("Fetching Transfer events from deployment block...\n");

    const deployBlock = 40908199;  // From deployment-base-mainnet.json
    const currentBlock = await provider.getBlockNumber();

    // Query transfer events
    const filter = token.filters.Transfer();
    const events = await token.queryFilter(filter, deployBlock, currentBlock);

    console.log("Total Transfer events:", events.length, "\n");

    // Track all unique addresses that received tokens
    const recipients = new Set();
    const transfers = [];

    for (const event of events) {
        const from = event.args[0];
        const to = event.args[1];
        const value = event.args[2];

        recipients.add(to);
        if (from !== ethers.ZeroAddress) {
            recipients.add(from);
        }

        transfers.push({
            from: from,
            to: to,
            value: ethers.formatUnits(value, 18),
            block: event.blockNumber,
            tx: event.transactionHash
        });
    }

    console.log("═══════════════════════════════════════════════════");
    console.log("ALL TRANSFER EVENTS:");
    console.log("═══════════════════════════════════════════════════\n");

    for (const t of transfers) {
        const fromLabel = KNOWN_ADDRESSES[t.from] || t.from.slice(0, 10) + "...";
        const toLabel = KNOWN_ADDRESSES[t.to] || t.to.slice(0, 10) + "...";
        console.log(`${fromLabel} → ${toLabel}: ${t.value} QCI`);
        console.log(`  Block: ${t.block} | Tx: ${t.tx.slice(0, 20)}...`);
        console.log("");
    }

    console.log("═══════════════════════════════════════════════════");
    console.log("ALL UNIQUE ADDRESSES WITH QCI:");
    console.log("═══════════════════════════════════════════════════\n");

    for (const addr of recipients) {
        if (addr === ethers.ZeroAddress) continue;

        const balance = await token.balanceOf(addr);
        const label = KNOWN_ADDRESSES[addr] || "UNKNOWN";
        const balanceFormatted = ethers.formatUnits(balance, 18);

        if (parseFloat(balanceFormatted) > 0 || KNOWN_ADDRESSES[addr]) {
            console.log(`${label}:`);
            console.log(`  Address: ${addr}`);
            console.log(`  Balance: ${balanceFormatted} QCI`);

            if (label === "UNKNOWN") {
                console.log(`  ⚠️  THIS IS ONE OF THE 2 NEW HOLDERS`);
            }
            console.log("");
        }
    }
}

traceHolders().catch(console.error);
