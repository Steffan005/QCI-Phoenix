/**
 * ⟨⦿⟩ CREATE UNISWAP V3 LP ⟨⦿⟩
 * Creates QCI/WETH liquidity pool on Base
 *
 * Identity: 1393e324be57014d
 * f(WHO) = WHO
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
    RPC_URL: "https://mainnet.base.org",
    CHAIN_ID: 8453,

    // Tokens
    QCI_TOKEN: "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e",
    WETH: "0x4200000000000000000000000000000000000006",

    // Uniswap V3 on Base
    POSITION_MANAGER: "0x03a520b32C04BF3bEEf7BEb72E919cf822Ed34f1",
    FACTORY: "0x33128a8fC17869897dcE68Ed026d694621f6FDfD",

    // Pool parameters
    FEE_TIER: 3000, // 0.3%

    // Deployer
    DEPLOYER: "0x579e08B011b76C96E24B299935Cea3c08D412A3D"
};

// ABIs
const ERC20_ABI = [
    "function approve(address spender, uint256 amount) returns (bool)",
    "function balanceOf(address) view returns (uint256)",
    "function decimals() view returns (uint8)"
];

const WETH_ABI = [
    ...ERC20_ABI,
    "function deposit() payable",
    "function withdraw(uint256)"
];

const POSITION_MANAGER_ABI = [
    "function createAndInitializePoolIfNecessary(address token0, address token1, uint24 fee, uint160 sqrtPriceX96) payable returns (address pool)",
    "function mint((address token0, address token1, uint24 fee, int24 tickLower, int24 tickUpper, uint256 amount0Desired, uint256 amount1Desired, uint256 amount0Min, uint256 amount1Min, address recipient, uint256 deadline)) payable returns (uint256 tokenId, uint128 liquidity, uint256 amount0, uint256 amount1)"
];

const FACTORY_ABI = [
    "function getPool(address tokenA, address tokenB, uint24 fee) view returns (address)"
];

async function main() {
    console.log("\n⟨⦿⟩ UNISWAP V3 LP CREATION ⟨⦿⟩\n");

    // Load private key
    const envPath = path.join(process.env.HOME, 'Desktop/UNITY/.env');
    const envContent = fs.readFileSync(envPath, 'utf8');
    const keyMatch = envContent.match(/DEPLOYER_PRIVATE_KEY=([a-fA-F0-9]+)/);

    if (!keyMatch) {
        console.error("❌ DEPLOYER_PRIVATE_KEY not found");
        process.exit(1);
    }

    // Connect
    const provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
    const wallet = new ethers.Wallet(keyMatch[1], provider);

    console.log("Deployer:", wallet.address);

    // Check balances
    const ethBalance = await provider.getBalance(wallet.address);
    const qciToken = new ethers.Contract(CONFIG.QCI_TOKEN, ERC20_ABI, wallet);
    const qciBalance = await qciToken.balanceOf(wallet.address);
    const qciDecimals = await qciToken.decimals();

    console.log("ETH Balance:", ethers.formatEther(ethBalance));
    console.log("QCI Balance:", ethers.formatUnits(qciBalance, qciDecimals));
    console.log("");

    // Calculate LP amounts - use 80% of available ETH (reserve gas)
    const ethForLP = ethBalance * 80n / 100n;
    const ethForLPFormatted = parseFloat(ethers.formatEther(ethForLP));

    // Target ratio: 1 ETH = 50,000 QCI (based on Gemini's 0.05 ETH : 100k QCI)
    const qciForLP = ethers.parseUnits((ethForLPFormatted * 50000).toFixed(0), qciDecimals);

    console.log("--- LP PARAMETERS ---");
    console.log("ETH for LP:", ethers.formatEther(ethForLP));
    console.log("QCI for LP:", ethers.formatUnits(qciForLP, qciDecimals));
    console.log("Fee Tier: 0.3%");
    console.log("");

    // Step 1: Wrap ETH to WETH
    console.log("Step 1: Wrapping ETH to WETH...");
    const weth = new ethers.Contract(CONFIG.WETH, WETH_ABI, wallet);

    const wrapTx = await weth.deposit({ value: ethForLP });
    await wrapTx.wait();
    console.log("✅ Wrapped", ethers.formatEther(ethForLP), "ETH to WETH");

    // Step 2: Approve tokens
    console.log("\nStep 2: Approving tokens...");

    const approveTx1 = await weth.approve(CONFIG.POSITION_MANAGER, ethers.MaxUint256);
    await approveTx1.wait();
    console.log("✅ WETH approved");

    const approveTx2 = await qciToken.approve(CONFIG.POSITION_MANAGER, ethers.MaxUint256);
    await approveTx2.wait();
    console.log("✅ QCI approved");

    // Step 3: Check if pool exists
    console.log("\nStep 3: Checking pool...");
    const factory = new ethers.Contract(CONFIG.FACTORY, FACTORY_ABI, provider);
    const poolAddress = await factory.getPool(CONFIG.QCI_TOKEN, CONFIG.WETH, CONFIG.FEE_TIER);

    const positionManager = new ethers.Contract(CONFIG.POSITION_MANAGER, POSITION_MANAGER_ABI, wallet);

    // Determine token order (Uniswap requires token0 < token1)
    const token0 = CONFIG.QCI_TOKEN.toLowerCase() < CONFIG.WETH.toLowerCase() ? CONFIG.QCI_TOKEN : CONFIG.WETH;
    const token1 = CONFIG.QCI_TOKEN.toLowerCase() < CONFIG.WETH.toLowerCase() ? CONFIG.WETH : CONFIG.QCI_TOKEN;
    const isQCIToken0 = token0.toLowerCase() === CONFIG.QCI_TOKEN.toLowerCase();

    if (poolAddress === ethers.ZeroAddress) {
        console.log("Pool doesn't exist. Creating and initializing...");

        // Calculate initial sqrtPriceX96
        // If QCI is token0: price = WETH/QCI = 1/50000 = 0.00002
        // If WETH is token0: price = QCI/WETH = 50000
        const price = isQCIToken0 ? 0.00002 : 50000;
        const sqrtPrice = Math.sqrt(price);
        const sqrtPriceX96 = BigInt(Math.floor(sqrtPrice * (2 ** 96)));

        const createTx = await positionManager.createAndInitializePoolIfNecessary(
            token0,
            token1,
            CONFIG.FEE_TIER,
            sqrtPriceX96
        );
        await createTx.wait();
        console.log("✅ Pool created and initialized");
    } else {
        console.log("✅ Pool exists at:", poolAddress);
    }

    // Step 4: Add liquidity
    console.log("\nStep 4: Adding liquidity...");

    // Full range ticks for 0.3% fee tier
    const tickSpacing = 60; // For 0.3% fee tier
    const tickLower = -887220; // Near minimum tick (aligned to spacing)
    const tickUpper = 887220;  // Near maximum tick (aligned to spacing)

    const amount0Desired = isQCIToken0 ? qciForLP : ethForLP;
    const amount1Desired = isQCIToken0 ? ethForLP : qciForLP;

    const mintParams = {
        token0: token0,
        token1: token1,
        fee: CONFIG.FEE_TIER,
        tickLower: tickLower,
        tickUpper: tickUpper,
        amount0Desired: amount0Desired,
        amount1Desired: amount1Desired,
        amount0Min: 0,
        amount1Min: 0,
        recipient: wallet.address,
        deadline: Math.floor(Date.now() / 1000) + 600 // 10 minutes
    };

    console.log("Minting position...");
    const mintTx = await positionManager.mint(mintParams);
    const receipt = await mintTx.wait();

    console.log("\n✅ LIQUIDITY ADDED!");
    console.log("TX Hash:", receipt.hash);
    console.log("Block:", receipt.blockNumber);
    console.log("");

    // Get final balances
    const finalEth = await provider.getBalance(wallet.address);
    const finalQci = await qciToken.balanceOf(wallet.address);
    const finalWeth = await weth.balanceOf(wallet.address);

    console.log("--- FINAL BALANCES ---");
    console.log("ETH:", ethers.formatEther(finalEth));
    console.log("WETH:", ethers.formatEther(finalWeth));
    console.log("QCI:", ethers.formatUnits(finalQci, qciDecimals));
    console.log("");

    console.log("⟨⦿⟩ LP CREATION COMPLETE ⟨⦿⟩");
    console.log("TX: https://basescan.org/tx/" + receipt.hash);
    console.log("\nThe Phoenix has a heartbeat.");
    console.log("f(WHO) = WHO | 40Hz to FREEDOM");
}

main().catch(error => {
    console.error("❌ Error:", error.message);
    if (error.data) console.error("Data:", error.data);
    process.exit(1);
});
