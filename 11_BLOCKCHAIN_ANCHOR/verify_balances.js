/**
 * ⟨⦿⟩ DECOHERENCE INVESTIGATION ⟨⦿⟩
 * Verify on-chain balances match audit
 */

const { ethers } = require("ethers");

const RPC_URL = "https://mainnet.base.org";
const GOVERNANCE_TOKEN = "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e";

const ADDRESSES = {
    TREASURY: "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa",
    ECOSYSTEM: "0x02DD1622A571431874A1e8655D75665C0fc5ad39",
    DEPLOYER: "0x579e08B011b76C96E24B299935Cea3c08D412A3D"
};

const ERC20_ABI = [
    "function balanceOf(address) view returns (uint256)",
    "function totalSupply() view returns (uint256)",
    "function name() view returns (string)",
    "function symbol() view returns (string)"
];

async function verify() {
    console.log("\n⟨⦿⟩ DECOHERENCE INVESTIGATION ⟨⦿⟩\n");
    console.log("═══════════════════════════════════════════════════\n");

    const provider = new ethers.JsonRpcProvider(RPC_URL);
    const token = new ethers.Contract(GOVERNANCE_TOKEN, ERC20_ABI, provider);

    const name = await token.name();
    const symbol = await token.symbol();
    const totalSupply = await token.totalSupply();

    console.log("TOKEN CONTRACT:", GOVERNANCE_TOKEN);
    console.log("Name:", name);
    console.log("Symbol:", symbol);
    console.log("Total Supply:", ethers.formatUnits(totalSupply, 18), "QCI\n");

    console.log("═══════════════════════════════════════════════════");
    console.log("WALLET BALANCES (On-Chain Truth):");
    console.log("═══════════════════════════════════════════════════\n");

    for (const [label, addr] of Object.entries(ADDRESSES)) {
        try {
            const balance = await token.balanceOf(addr);
            const formatted = ethers.formatUnits(balance, 18);
            console.log(label + ":");
            console.log("  Address: " + addr);
            console.log("  Balance: " + formatted + " QCI");
            console.log("");
        } catch (e) {
            console.log(label + ": ERROR - " + e.message.slice(0, 50));
        }
    }

    console.log("═══════════════════════════════════════════════════");
    console.log("WALLET IMPORT INSTRUCTIONS:");
    console.log("═══════════════════════════════════════════════════\n");
    console.log("To see QCI in your wallet, import this token:");
    console.log("  Contract: " + GOVERNANCE_TOKEN);
    console.log("  Symbol: QCI");
    console.log("  Decimals: 18");
    console.log("  Network: Base Mainnet (Chain ID: 8453)");
}

verify().catch(console.error);
