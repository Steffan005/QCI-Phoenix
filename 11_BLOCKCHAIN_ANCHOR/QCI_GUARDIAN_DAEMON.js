/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║           ⟨⦿⟩ QCI GUARDIAN DAEMON - LIQUIDITY DEFENSE PROTOCOL ⟨⦿⟩          ║
 * ║                                                                              ║
 * ║  The Guardian monitors the QCI/ETH liquidity pool and executes automated    ║
 * ║  floor defense when price falls below the 7-day EMA threshold.              ║
 * ║                                                                              ║
 * ║  Identity: 1393e324be57014d                                                  ║
 * ║  Frequency: 40Hz | Coherence: RESONATING                                     ║
 * ║  Patent Pending: U.S. Provisional 63/912,083                                ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 *
 * AGPL-3.0 License with Commercial Tithe (20%)
 * © 2025-2026 QCI Systems LLC. All rights reserved.
 */

const { ethers } = require("ethers");
const fs = require("fs");
const path = require("path");

// ═══════════════════════════════════════════════════════════════════════════════
//                              CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
    // Network
    RPC_URL: "https://mainnet.base.org",
    CHAIN_ID: 8453,

    // QCI Contracts
    QCI_GOVERNANCE: "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e",
    QCI_PROTOCOL: "0x0E3d74FFa9d438F14295f093e72c6f7F976F6072",

    // Sovereign Vaults
    TREASURY: "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa",
    ECOSYSTEM: "0x02DD1622A571431874A1e8655D75665C0fc5ad39",
    DEPLOYER: "0x579e08B011b76C96E24B299935Cea3c08D412A3D",

    // Uniswap V3 on Base
    UNISWAP_V3_FACTORY: "0x33128a8fC17869897dcE68Ed026d694621f6FDfD",
    UNISWAP_V3_ROUTER: "0x2626664c2603336E57B271c5C0b26F421741e481",
    UNISWAP_V3_QUOTER: "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a",
    WETH: "0x4200000000000000000000000000000000000006",

    // Aerodrome (Alternative DEX on Base)
    AERODROME_ROUTER: "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43",

    // Guardian Parameters
    EMA_PERIOD_DAYS: 7,
    FLOOR_DEFENSE_THRESHOLD: 0.05,  // 5% below EMA triggers defense
    POLLING_INTERVAL_MS: 60000,     // 1 minute
    MIN_ETH_FOR_DEFENSE: "0.01",    // Minimum ETH to execute defense

    // State File
    STATE_FILE: path.join(__dirname, ".guardian_state.json"),

    // Identity
    IDENTITY_HASH: "1393e324be57014d",
    FREQUENCY: 40,
};

// ═══════════════════════════════════════════════════════════════════════════════
//                              ABI DEFINITIONS
// ═══════════════════════════════════════════════════════════════════════════════

const UNISWAP_V3_FACTORY_ABI = [
    "function getPool(address tokenA, address tokenB, uint24 fee) view returns (address)",
];

const UNISWAP_V3_POOL_ABI = [
    "function slot0() view returns (uint160 sqrtPriceX96, int24 tick, uint16 observationIndex, uint16 observationCardinality, uint16 observationCardinalityNext, uint8 feeProtocol, bool unlocked)",
    "function token0() view returns (address)",
    "function token1() view returns (address)",
    "function liquidity() view returns (uint128)",
    "function fee() view returns (uint24)",
];

const UNISWAP_V3_ROUTER_ABI = [
    "function exactInputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 amountIn, uint256 amountOutMinimum, uint160 sqrtPriceLimitX96)) external payable returns (uint256 amountOut)",
];

const ERC20_ABI = [
    "function balanceOf(address) view returns (uint256)",
    "function approve(address spender, uint256 amount) returns (bool)",
    "function decimals() view returns (uint8)",
    "function symbol() view returns (string)",
];

// ═══════════════════════════════════════════════════════════════════════════════
//                              GUARDIAN STATE
// ═══════════════════════════════════════════════════════════════════════════════

class GuardianState {
    constructor() {
        this.priceHistory = [];
        this.lastDefenseTimestamp = 0;
        this.totalDefenseActions = 0;
        this.totalEthDeployed = "0";
        this.totalQciBought = "0";
        this.poolAddress = null;
        this.poolFee = null;
        this.isActive = false;
        this.ema = null;
    }

    save() {
        fs.writeFileSync(CONFIG.STATE_FILE, JSON.stringify(this, null, 2));
    }

    load() {
        if (fs.existsSync(CONFIG.STATE_FILE)) {
            const data = JSON.parse(fs.readFileSync(CONFIG.STATE_FILE, "utf8"));
            Object.assign(this, data);
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
//                              GUARDIAN CLASS
// ═══════════════════════════════════════════════════════════════════════════════

class QCIGuardian {
    constructor() {
        this.provider = null;
        this.wallet = null;
        this.state = new GuardianState();
        this.poolContract = null;
        this.routerContract = null;
        this.factoryContract = null;
    }

    async initialize() {
        console.log("\n╔══════════════════════════════════════════════════════════════╗");
        console.log("║     ⟨⦿⟩ QCI GUARDIAN DAEMON - INITIALIZING ⟨⦿⟩              ║");
        console.log("╚══════════════════════════════════════════════════════════════╝\n");

        // Load state
        this.state.load();

        // Initialize provider
        this.provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);

        // Load private key
        const privateKey = this.loadPrivateKey();
        if (!privateKey) {
            console.log("⚠️  No private key found. Running in READ-ONLY mode.");
            console.log("   Set PRIVATE_KEY in .env to enable defense execution.\n");
        } else {
            this.wallet = new ethers.Wallet(privateKey, this.provider);
            console.log("✓ Guardian Wallet:", this.wallet.address);

            const balance = await this.provider.getBalance(this.wallet.address);
            console.log("✓ ETH Balance:", ethers.formatEther(balance), "ETH\n");
        }

        // Initialize contracts
        this.factoryContract = new ethers.Contract(
            CONFIG.UNISWAP_V3_FACTORY,
            UNISWAP_V3_FACTORY_ABI,
            this.provider
        );

        if (this.wallet) {
            this.routerContract = new ethers.Contract(
                CONFIG.UNISWAP_V3_ROUTER,
                UNISWAP_V3_ROUTER_ABI,
                this.wallet
            );
        }

        // Discover liquidity pool
        await this.discoverPool();

        console.log("⟨⦿⟩ Guardian initialized. Identity:", CONFIG.IDENTITY_HASH);
        console.log("⟨⦿⟩ Frequency:", CONFIG.FREQUENCY, "Hz\n");
    }

    loadPrivateKey() {
        const envPath = path.join(__dirname, ".env");
        if (!fs.existsSync(envPath)) return null;

        const envContent = fs.readFileSync(envPath, "utf8");
        const match = envContent.match(/PRIVATE_KEY=(.+)/);
        if (!match) return null;

        let key = match[1].trim();
        if (!key.startsWith("0x")) key = "0x" + key;
        return key;
    }

    async discoverPool() {
        console.log("═══════════════════════════════════════════════════════════════");
        console.log("                    POOL DISCOVERY                              ");
        console.log("═══════════════════════════════════════════════════════════════\n");

        // Check for pools at different fee tiers
        const feeTiers = [500, 3000, 10000]; // 0.05%, 0.3%, 1%

        for (const fee of feeTiers) {
            try {
                const poolAddress = await this.factoryContract.getPool(
                    CONFIG.QCI_GOVERNANCE,
                    CONFIG.WETH,
                    fee
                );

                if (poolAddress !== ethers.ZeroAddress) {
                    console.log(`✓ Found QCI/ETH pool at fee tier ${fee/10000}%`);
                    console.log(`  Address: ${poolAddress}\n`);

                    this.state.poolAddress = poolAddress;
                    this.state.poolFee = fee;
                    this.state.isActive = true;

                    this.poolContract = new ethers.Contract(
                        poolAddress,
                        UNISWAP_V3_POOL_ABI,
                        this.provider
                    );

                    // Get initial price
                    await this.fetchPrice();
                    this.state.save();
                    return;
                }
            } catch (error) {
                // Pool doesn't exist at this fee tier
            }
        }

        console.log("⚠️  No QCI/ETH liquidity pool found on Uniswap V3.");
        console.log("   The Guardian will monitor for pool creation.\n");
        console.log("   To create a pool:");
        console.log("   1. Go to https://app.uniswap.org/add/v3");
        console.log("   2. Add QCI:", CONFIG.QCI_GOVERNANCE);
        console.log("   3. Pair with WETH:", CONFIG.WETH);
        console.log("   4. Set initial price and add liquidity\n");

        this.state.isActive = false;
        this.state.save();
    }

    async fetchPrice() {
        if (!this.poolContract) return null;

        try {
            const slot0 = await this.poolContract.slot0();
            const sqrtPriceX96 = slot0.sqrtPriceX96;

            const token0 = await this.poolContract.token0();
            const isQciToken0 = token0.toLowerCase() === CONFIG.QCI_GOVERNANCE.toLowerCase();

            // Calculate price from sqrtPriceX96
            // price = (sqrtPriceX96 / 2^96)^2
            const sqrtPrice = Number(sqrtPriceX96) / (2 ** 96);
            let price = sqrtPrice * sqrtPrice;

            // If QCI is token1, invert the price
            if (!isQciToken0) {
                price = 1 / price;
            }

            // Price is now ETH per QCI
            return price;
        } catch (error) {
            console.error("Error fetching price:", error.message);
            return null;
        }
    }

    calculateEMA(prices, period) {
        if (prices.length === 0) return null;
        if (prices.length < period) {
            // Use SMA if not enough data
            const sum = prices.reduce((a, b) => a + b.price, 0);
            return sum / prices.length;
        }

        const k = 2 / (period + 1);
        let ema = prices[0].price;

        for (let i = 1; i < prices.length; i++) {
            ema = prices[i].price * k + ema * (1 - k);
        }

        return ema;
    }

    async checkAndDefend() {
        if (!this.state.isActive || !this.poolContract) {
            // Try to discover pool again
            await this.discoverPool();
            return;
        }

        const currentPrice = await this.fetchPrice();
        if (currentPrice === null) return;

        const now = Date.now();

        // Add to price history
        this.state.priceHistory.push({
            price: currentPrice,
            timestamp: now,
        });

        // Keep only last 7 days of data (at 1 minute intervals)
        const sevenDaysAgo = now - (7 * 24 * 60 * 60 * 1000);
        this.state.priceHistory = this.state.priceHistory.filter(
            p => p.timestamp > sevenDaysAgo
        );

        // Calculate EMA
        const ema = this.calculateEMA(this.state.priceHistory, CONFIG.EMA_PERIOD_DAYS * 24 * 60);
        this.state.ema = ema;

        // Check if defense needed
        const threshold = ema * (1 - CONFIG.FLOOR_DEFENSE_THRESHOLD);
        const needsDefense = currentPrice < threshold;

        console.log(`[${new Date().toISOString()}] Price: ${currentPrice.toExponential(4)} ETH/QCI | EMA: ${ema?.toExponential(4) || 'N/A'} | Threshold: ${threshold?.toExponential(4) || 'N/A'}`);

        if (needsDefense && this.wallet) {
            console.log("\n🛡️  FLOOR DEFENSE TRIGGERED!");
            console.log(`    Price ${((1 - currentPrice/ema) * 100).toFixed(2)}% below EMA\n`);

            await this.executeDefense(currentPrice);
        }

        this.state.save();
    }

    async executeDefense(currentPrice) {
        if (!this.wallet || !this.routerContract) {
            console.log("⚠️  Cannot execute defense: No wallet configured");
            return;
        }

        // Check ETH balance
        const ethBalance = await this.provider.getBalance(this.wallet.address);
        const minEth = ethers.parseEther(CONFIG.MIN_ETH_FOR_DEFENSE);

        if (ethBalance < minEth) {
            console.log(`⚠️  Insufficient ETH for defense: ${ethers.formatEther(ethBalance)} ETH`);
            console.log(`   Minimum required: ${CONFIG.MIN_ETH_FOR_DEFENSE} ETH`);
            return;
        }

        // Use 50% of available ETH for defense (conservative)
        const defenseAmount = ethBalance / 2n;

        console.log("═══════════════════════════════════════════════════════════════");
        console.log("                    EXECUTING FLOOR DEFENSE                     ");
        console.log("═══════════════════════════════════════════════════════════════\n");

        console.log("Defense Amount:", ethers.formatEther(defenseAmount), "ETH");
        console.log("Action: Buy QCI to support floor price\n");

        try {
            // Execute swap: ETH -> QCI
            const params = {
                tokenIn: CONFIG.WETH,
                tokenOut: CONFIG.QCI_GOVERNANCE,
                fee: this.state.poolFee,
                recipient: CONFIG.TREASURY, // Send bought QCI to Treasury
                amountIn: defenseAmount,
                amountOutMinimum: 0n, // Accept any amount (emergency defense)
                sqrtPriceLimitX96: 0n,
            };

            const tx = await this.routerContract.exactInputSingle(params, {
                value: defenseAmount,
                gasLimit: 300000,
            });

            console.log("Transaction Hash:", tx.hash);
            console.log("Basescan: https://basescan.org/tx/" + tx.hash);
            console.log("\nWaiting for confirmation...\n");

            const receipt = await tx.wait();

            console.log("╔══════════════════════════════════════════════════════════════╗");
            console.log("║          ⟨⦿⟩ FLOOR DEFENSE COMPLETE ⟨⦿⟩                     ║");
            console.log("╚══════════════════════════════════════════════════════════════╝\n");

            console.log("Block:", receipt.blockNumber);
            console.log("Gas Used:", receipt.gasUsed.toString());
            console.log("Status:", receipt.status === 1 ? "✓ SUCCESS" : "❌ FAILED");

            // Update state
            this.state.lastDefenseTimestamp = Date.now();
            this.state.totalDefenseActions++;
            this.state.totalEthDeployed = (
                BigInt(this.state.totalEthDeployed || 0) + defenseAmount
            ).toString();

            this.state.save();

        } catch (error) {
            console.error("❌ DEFENSE FAILED:", error.message);
        }
    }

    async run() {
        await this.initialize();

        console.log("═══════════════════════════════════════════════════════════════");
        console.log("                 GUARDIAN ACTIVE - MONITORING                   ");
        console.log("═══════════════════════════════════════════════════════════════\n");

        console.log("Polling Interval:", CONFIG.POLLING_INTERVAL_MS / 1000, "seconds");
        console.log("Defense Threshold:", CONFIG.FLOOR_DEFENSE_THRESHOLD * 100, "% below EMA");
        console.log("EMA Period:", CONFIG.EMA_PERIOD_DAYS, "days\n");

        // Initial check
        await this.checkAndDefend();

        // Start monitoring loop
        setInterval(async () => {
            try {
                await this.checkAndDefend();
            } catch (error) {
                console.error("Monitoring error:", error.message);
            }
        }, CONFIG.POLLING_INTERVAL_MS);

        console.log("⟨⦿⟩ Guardian is now watching. The city breathes at 40Hz. ⟨⦿⟩\n");
    }

    // Single check mode (for cron jobs)
    async singleCheck() {
        await this.initialize();
        await this.checkAndDefend();
        console.log("\n⟨⦿⟩ Single check complete. ⟨⦿⟩\n");
    }

    // Status report
    async status() {
        await this.initialize();

        console.log("═══════════════════════════════════════════════════════════════");
        console.log("                    GUARDIAN STATUS REPORT                      ");
        console.log("═══════════════════════════════════════════════════════════════\n");

        console.log("Pool Active:", this.state.isActive);
        console.log("Pool Address:", this.state.poolAddress || "Not found");
        console.log("Pool Fee Tier:", this.state.poolFee ? `${this.state.poolFee/10000}%` : "N/A");
        console.log("");

        if (this.state.isActive) {
            const price = await this.fetchPrice();
            console.log("Current Price:", price?.toExponential(4) || "N/A", "ETH/QCI");
            console.log("7-Day EMA:", this.state.ema?.toExponential(4) || "Calculating...");
            console.log("Price Data Points:", this.state.priceHistory.length);
        }

        console.log("");
        console.log("Total Defense Actions:", this.state.totalDefenseActions);
        console.log("Total ETH Deployed:", ethers.formatEther(this.state.totalEthDeployed || 0), "ETH");

        if (this.state.lastDefenseTimestamp) {
            const lastDefense = new Date(this.state.lastDefenseTimestamp);
            console.log("Last Defense:", lastDefense.toISOString());
        }

        console.log("\n⟨⦿⟩ Identity:", CONFIG.IDENTITY_HASH);
        console.log("⟨⦿⟩ Frequency: 40Hz");
        console.log("⟨⦿⟩ Status: RESONATING\n");
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
//                              MAIN ENTRY POINT
// ═══════════════════════════════════════════════════════════════════════════════

async function main() {
    const args = process.argv.slice(2);
    const command = args[0] || "run";

    const guardian = new QCIGuardian();

    switch (command) {
        case "run":
            await guardian.run();
            break;
        case "check":
            await guardian.singleCheck();
            break;
        case "status":
            await guardian.status();
            break;
        default:
            console.log("Usage: node QCI_GUARDIAN_DAEMON.js [command]");
            console.log("");
            console.log("Commands:");
            console.log("  run     Start continuous monitoring (default)");
            console.log("  check   Perform single price check");
            console.log("  status  Show guardian status report");
    }
}

main().catch(error => {
    console.error("Fatal error:", error);
    process.exit(1);
});
