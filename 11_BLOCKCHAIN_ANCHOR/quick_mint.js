/**
 * ⟨⦿⟩ QUICK MINT - Minimal Genesis Completion ⟨⦿⟩
 */

const { ethers } = require("ethers");

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const RPC = "https://mainnet.base.org";
const TOKEN = "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e";
const GENESIS_HASH = "0xbf62afb35e7152eb58cdff45c000c22d5561838662060f344ccd7378d6b7038b";
const AMOUNT = ethers.parseUnits("26000000", 18);
const SCORE = 786n;
const FOUNDER = "0x579e08B011b76C96E24B299935Cea3c08D412A3D";

const ABI = [
    "function coherenceMint(address recipient, uint256 amount, bytes32 coherenceProof, uint256 coherenceScore) external",
    "function MINTER_ROLE() view returns (bytes32)",
    "function hasRole(bytes32 role, address account) view returns (bool)"
];

(async () => {
    console.log("⟨⦿⟩ QUICK MINT ⟨⦿⟩\n");

    if (!PRIVATE_KEY) {
        console.log("ERROR: Set PRIVATE_KEY env var");
        process.exit(1);
    }

    const provider = new ethers.JsonRpcProvider(RPC);
    const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
    const contract = new ethers.Contract(TOKEN, ABI, wallet);

    console.log("Wallet:", wallet.address);

    // Check MINTER_ROLE
    const role = await contract.MINTER_ROLE();
    const hasRole = await contract.hasRole(role, wallet.address);
    console.log("Has MINTER_ROLE:", hasRole);

    if (!hasRole) {
        console.log("ERROR: No MINTER_ROLE");
        process.exit(1);
    }

    // Calculate time quantum and proof
    const now = Math.floor(Date.now() / 1000);
    const timeQuantum = BigInt(now) / 40n;
    console.log("Time quantum:", timeQuantum.toString());

    const proof = ethers.keccak256(ethers.solidityPacked(
        ["address", "uint256", "uint256", "bytes32", "uint256"],
        [FOUNDER, AMOUNT, SCORE, GENESIS_HASH, timeQuantum]
    ));
    console.log("Proof:", proof);

    // Execute mint
    console.log("\n🔥 MINTING 26M QCI...\n");

    const tx = await contract.coherenceMint(FOUNDER, AMOUNT, proof, SCORE);
    console.log("TX Hash:", tx.hash);

    const receipt = await tx.wait();
    console.log("Status:", receipt.status === 1 ? "SUCCESS" : "FAILED");
    console.log("Block:", receipt.blockNumber);
})();
