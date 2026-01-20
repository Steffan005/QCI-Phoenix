/**
 * ⟨⦿⟩ QCI GUARDIAN DAEMON ⟨⦿⟩
 * Automated Liquidity Defense for QCI Phoenix
 *
 * Identity: 1393e324be57014d
 * Frequency: 40Hz
 *
 * The Guardian watches the pool.
 * When price falls >5% below 7-day EMA, the Guardian defends.
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// ═══════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

const CONFIG = {
    // Network
    RPC_URL: "https://mainnet.base.org",
    CHAIN_ID: 8453,

    // Contracts
    QCI_GOVERNANCE: "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e",
    TREASURY: "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa",
    DEPLOYER: "0x579e08B011b76C96E24B299935Cea3c08D412A3D",
    WETH: "0x4200000000000000000000000000000000000006",

    // Uniswap V3 on Base
    UNISWAP_V3_FACTORY: "0x33128a8fC17869897dcE68Ed026d694621f6FDfD",
    UNISWAP_V3_ROUTER: "0x2626664c2603336E57B271c5C0b26F421741e481",
    UNISWAP_V3_QUOTER: "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a",
    FEE_TIER: 3000, // 0.3%

    // Guardian Parameters
    EMA_PERIOD_DAYS: 7,
    FLOOR_DEFENSE_THRESHOLD: 0.05,  // 5% below EMA triggers defense
    MIN_DEFENSE_ETH: 0.01,          // Minimum ETH to deploy in defense
    MAX_DEFENSE_ETH: 0.5,           // Maximum ETH per defense action

    // Operational
    POLLING_INTERVAL_MS: 60000,     // Check every 60 seconds
    PRICE_HISTORY_FILE: "/tmp/qci_price_history.json",
    GUARDIAN_LOG_FILE: "/tmp/guardian.log",

    // Identity
    IDENTITY: "1393e324be57014d",
    FREQUENCY: "40Hz"
};

// ═══════════════════════════════════════════════════════════════════════════
// ABIs (Minimal)
// ═══════════════════════════════════════════════════════════════════════════

const ERC20_ABI = [
    "function balanceOf(address) view returns (uint256)",
    "function decimals() view returns (uint8)",
    "function approve(address spender, uint256 amount) returns (bool)",
    "function transfer(address to, uint256 amount) returns (bool)"
];

const UNISWAP_V3_FACTORY_ABI = [
    "function getPool(address tokenA, address tokenB, uint24 fee) view returns (address)"
];

const UNISWAP_V3_POOL_ABI = [
    "function slot0() view returns (uint160 sqrtPriceX96, int24 tick, uint16 observationIndex, uint16 observationCardinality, uint16 observationCardinalityNext, uint8 feeProtocol, bool unlocked)",
    "function token0() view returns (address)",
    "function token1() view returns (address)"
];

const UNISWAP_V3_ROUTER_ABI = [
    "function exactInputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 deadline, uint256 amountIn, uint256 amountOutMinimum, uint160 sqrtPriceLimitX96)) payable returns (uint256 amountOut)"
];

// ═══════════════════════════════════════════════════════════════════════════
// GUARDIAN CLASS
// ═══════════════════════════════════════════════════════════════════════════

class QCIGuardian {
    constructor() {
        this.provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);
        this.priceHistory = [];
        this.poolAddress = null;
        this.isToken0QCI = false;

        // Load private key from environment
        const envPath = path.join(process.env.HOME, 'Desktop/UNITY/.env');
        if (fs.existsSync(envPath)) {
            const envContent = fs.readFileSync(envPath, 'utf8');
            const match = envContent.match(/DEPLOYER_PRIVATE_KEY=(\w+)/);
            if (match) {
                this.wallet = new ethers.Wallet(match[1], this.provider);
                this.log(`Wallet loaded: ${this.wallet.address}`);
            }
        }

        // Load price history
        this.loadPriceHistory();
    }

    log(message) {
        const timestamp = new Date().toISOString();
        const logLine = `[${timestamp}] [GUARDIAN] ${message}`;
        console.log(logLine);

        try {
            fs.appendFileSync(CONFIG.GUARDIAN_LOG_FILE, logLine + '\n');
        } catch (e) {}
    }

    loadPriceHistory() {
        try {
            if (fs.existsSync(CONFIG.PRICE_HISTORY_FILE)) {
                this.priceHistory = JSON.parse(fs.readFileSync(CONFIG.PRICE_HISTORY_FILE, 'utf8'));
                this.log(`Loaded ${this.priceHistory.length} historical prices`);
            }
        } catch (e) {
            this.priceHistory = [];
        }
    }

    savePriceHistory() {
        try {
            // Keep only last 7 days of minute-by-minute data
            const cutoff = Date.now() - (CONFIG.EMA_PERIOD_DAYS * 24 * 60 * 60 * 1000);
            this.priceHistory = this.priceHistory.filter(p => p.timestamp > cutoff);
            fs.writeFileSync(CONFIG.PRICE_HISTORY_FILE, JSON.stringify(this.priceHistory, null, 2));
        } catch (e) {
            this.log(`Error saving price history: ${e.message}`);
        }
    }

    async getPoolAddress() {
        if (this.poolAddress) return this.poolAddress;

        const factory = new ethers.Contract(CONFIG.UNISWAP_V3_FACTORY, UNISWAP_V3_FACTORY_ABI, this.provider);
        this.poolAddress = await factory.getPool(CONFIG.QCI_GOVERNANCE, CONFIG.WETH, CONFIG.FEE_TIER);

        if (this.poolAddress === ethers.ZeroAddress) {
            this.log("Pool does not exist yet!");
            return null;
        }

        // Determine token order
        const pool = new ethers.Contract(this.poolAddress, UNISWAP_V3_POOL_ABI, this.provider);
        const token0 = await pool.token0();
        this.isToken0QCI = token0.toLowerCase() === CONFIG.QCI_GOVERNANCE.toLowerCase();

        this.log(`Pool found: ${this.poolAddress}`);
        this.log(`QCI is token${this.isToken0QCI ? '0' : '1'}`);

        return this.poolAddress;
    }

    async getCurrentPrice() {
        const poolAddr = await this.getPoolAddress();
        if (!poolAddr) return null;

        const pool = new ethers.Contract(poolAddr, UNISWAP_V3_POOL_ABI, this.provider);
        const slot0 = await pool.slot0();
        const sqrtPriceX96 = slot0.sqrtPriceX96;

        // Calculate price from sqrtPriceX96
        // price = (sqrtPriceX96 / 2^96)^2
        const price = Number(sqrtPriceX96) ** 2 / (2 ** 192);

        // If QCI is token0, price is ETH/QCI, we want QCI/ETH
        // If QCI is token1, price is QCI/ETH
        const qciPriceInEth = this.isToken0QCI ? price : 1 / price;

        return qciPriceInEth;
    }

    calculateEMA(prices, period) {
        if (prices.length === 0) return null;
        if (prices.length < period) period = prices.length;

        const k = 2 / (period + 1);
        let ema = prices[0].price;

        for (let i = 1; i < prices.length; i++) {
            ema = prices[i].price * k + ema * (1 - k);
        }

        return ema;
    }

    async checkAndDefend() {
        try {
            const currentPrice = await this.getCurrentPrice();
            if (currentPrice === null) {
                this.log("No pool or price available");
                return;
            }

            // Record price
            this.priceHistory.push({
                timestamp: Date.now(),
                price: currentPrice
            });
            this.savePriceHistory();

            // Calculate 7-day EMA
            const ema = this.calculateEMA(this.priceHistory, CONFIG.EMA_PERIOD_DAYS * 24 * 60);

            if (ema === null) {
                this.log(`Current price: ${currentPrice.toExponential(4)} ETH/QCI (building EMA history)`);
                return;
            }

            const deviation = (currentPrice - ema) / ema;

            this.log(`Price: ${currentPrice.toExponential(4)} | EMA: ${ema.toExponential(4)} | Deviation: ${(deviation * 100).toFixed(2)}%`);

            // Check if defense is needed
            if (deviation < -CONFIG.FLOOR_DEFENSE_THRESHOLD) {
                this.log(`⚠️ FLOOR BREACH DETECTED! Price ${Math.abs(deviation * 100).toFixed(2)}% below EMA`);
                await this.executeDefense(currentPrice);
            }

        } catch (error) {
            this.log(`Error in check cycle: ${error.message}`);
        }
    }

    async executeDefense(currentPrice) {
        if (!this.wallet) {
            this.log("No wallet configured - cannot execute defense");
            return;
        }

        try {
            // Check ETH balance
            const ethBalance = await this.provider.getBalance(this.wallet.address);
            const ethBalanceNum = Number(ethers.formatEther(ethBalance));

            if (ethBalanceNum < CONFIG.MIN_DEFENSE_ETH) {
                this.log(`Insufficient ETH for defense: ${ethBalanceNum.toFixed(4)} ETH`);
                return;
            }

            // Calculate defense amount (use 50% of available, up to max)
            let defenseAmount = Math.min(ethBalanceNum * 0.5, CONFIG.MAX_DEFENSE_ETH);
            defenseAmount = Math.max(defenseAmount, CONFIG.MIN_DEFENSE_ETH);

            this.log(`🛡️ EXECUTING FLOOR DEFENSE: ${defenseAmount.toFixed(4)} ETH`);

            // Execute swap via Uniswap V3 Router
            const router = new ethers.Contract(CONFIG.UNISWAP_V3_ROUTER, UNISWAP_V3_ROUTER_ABI, this.wallet);

            const deadline = Math.floor(Date.now() / 1000) + 300; // 5 minutes
            const amountIn = ethers.parseEther(defenseAmount.toString());

            const params = {
                tokenIn: CONFIG.WETH,
                tokenOut: CONFIG.QCI_GOVERNANCE,
                fee: CONFIG.FEE_TIER,
                recipient: this.wallet.address,
                deadline: deadline,
                amountIn: amountIn,
                amountOutMinimum: 0, // Accept any amount (defense is priority)
                sqrtPriceLimitX96: 0
            };

            const tx = await router.exactInputSingle(params, { value: amountIn });
            this.log(`Defense TX submitted: ${tx.hash}`);

            const receipt = await tx.wait();
            this.log(`✅ DEFENSE COMPLETE! TX: ${receipt.hash} | Block: ${receipt.blockNumber}`);

            // Record to KAIROS
            this.recordToKairos(defenseAmount, receipt.hash);

        } catch (error) {
            this.log(`Defense execution failed: ${error.message}`);
        }
    }

    async recordToKairos(amount, txHash) {
        try {
            const memory = {
                content: `GUARDIAN DEFENSE EXECUTED: ${amount.toFixed(4)} ETH deployed to defend QCI floor. TX: ${txHash}`,
                significance: 0.95,
                source: "guardian_daemon"
            };

            // Try local KAIROS
            const response = await fetch('http://127.0.0.1:8056/kairos/remember', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(memory)
            });

            if (response.ok) {
                this.log("Defense recorded to KAIROS");
            }
        } catch (e) {
            // KAIROS might be down, that's ok
        }
    }

    async status() {
        console.log("\n⟨⦿⟩ QCI GUARDIAN STATUS ⟨⦿⟩\n");

        const poolAddr = await this.getPoolAddress();
        console.log(`Pool Address: ${poolAddr || 'NOT DEPLOYED'}`);

        if (poolAddr) {
            const price = await this.getCurrentPrice();
            console.log(`Current Price: ${price?.toExponential(4) || 'N/A'} ETH/QCI`);

            const ema = this.calculateEMA(this.priceHistory, CONFIG.EMA_PERIOD_DAYS * 24 * 60);
            console.log(`7-Day EMA: ${ema?.toExponential(4) || 'Building history...'}`);

            if (price && ema) {
                const deviation = ((price - ema) / ema) * 100;
                console.log(`Deviation: ${deviation.toFixed(2)}%`);
                console.log(`Defense Trigger: ${deviation < -5 ? '⚠️ ACTIVE' : '✅ Monitoring'}`);
            }
        }

        if (this.wallet) {
            const ethBalance = await this.provider.getBalance(this.wallet.address);
            console.log(`\nGuardian Wallet: ${this.wallet.address}`);
            console.log(`ETH Balance: ${ethers.formatEther(ethBalance)} ETH`);
        }

        console.log(`\nPrice History: ${this.priceHistory.length} data points`);
        console.log(`Identity: ${CONFIG.IDENTITY}`);
        console.log(`Frequency: ${CONFIG.FREQUENCY}`);
        console.log("\n⟨⦿⟩ The Guardian watches. ⟨⦿⟩\n");
    }

    async run() {
        console.log("\n" + "═".repeat(70));
        console.log("⟨⦿⟩ QCI GUARDIAN DAEMON - ACTIVATED ⟨⦿⟩");
        console.log("═".repeat(70));
        console.log(`Identity: ${CONFIG.IDENTITY}`);
        console.log(`Frequency: ${CONFIG.FREQUENCY}`);
        console.log(`Defense Threshold: ${CONFIG.FLOOR_DEFENSE_THRESHOLD * 100}% below EMA`);
        console.log(`Polling Interval: ${CONFIG.POLLING_INTERVAL_MS / 1000}s`);
        console.log("═".repeat(70) + "\n");

        // Initial check
        await this.checkAndDefend();

        // Start monitoring loop
        setInterval(() => this.checkAndDefend(), CONFIG.POLLING_INTERVAL_MS);

        this.log("Guardian daemon running. Press Ctrl+C to stop.");
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

const guardian = new QCIGuardian();

const command = process.argv[2];

switch (command) {
    case 'status':
        guardian.status();
        break;
    case 'run':
        guardian.run();
        break;
    default:
        console.log("Usage: node QCI_GUARDIAN_DAEMON.js [status|run]");
        console.log("  status - Show current pool and guardian status");
        console.log("  run    - Start the guardian daemon");
}
