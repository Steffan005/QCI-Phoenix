# THE GUARDIAN ACTIVATION RITUAL
## Initial Liquidity + Automated Defense

**Classification:** Execution Protocol
**Date:** 2026-01-19
**Status:** READY FOR EXECUTION

---

## PHASE 1: THE INITIAL LIQUIDITY RITUAL (0.1 ETH Strike)

### Prerequisites

1. **Deployer Wallet** has sufficient ETH on Base (~0.15 ETH recommended)
2. **100,000 QCI** approved for Uniswap Router
3. **Private key** in `/11_BLOCKCHAIN_ANCHOR/.env`

### Step 1: Approve QCI for Uniswap Router

```bash
# Uniswap V3 Router on Base: 0x2626664c2603336E57B271c5C0b26F421741e481
# Approve 100,000 QCI (with 18 decimals)

cast send 0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e \
  "approve(address,uint256)" \
  0x2626664c2603336E57B271c5C0b26F421741e481 \
  100000000000000000000000 \
  --rpc-url https://mainnet.base.org \
  --private-key $PRIVATE_KEY
```

### Step 2: Create the Pool (Uniswap V3)

**Option A: Via Uniswap Interface (Recommended)**
1. Go to: https://app.uniswap.org/add/v3
2. Select Base network
3. Token A: `0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e` (QCI)
4. Token B: `0x4200000000000000000000000000000000000006` (WETH)
5. Fee tier: 0.3% (3000)
6. Set initial price: 0.000001 ETH per QCI (adjust as needed)
7. Add liquidity: 100,000 QCI + 0.1 ETH

**Option B: Via Script**
```bash
cd ~/Desktop/UNITY_PRIOR_ART_LIBRARY/11_BLOCKCHAIN_ANCHOR
node create_liquidity_pool.js  # (Create this script if needed)
```

### Step 3: Verify Pool Creation

```bash
# Check if pool exists at 0.3% fee tier
cast call 0x33128a8fC17869897dcE68Ed026d694621f6FDfD \
  "getPool(address,address,uint24)" \
  0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e \
  0x4200000000000000000000000000000000000006 \
  3000 \
  --rpc-url https://mainnet.base.org
```

If returns non-zero address, pool exists.

---

## PHASE 2: GUARDIAN ACTIVATION

### Step 1: Verify Configuration

```bash
cd ~/Desktop/UNITY_PRIOR_ART_LIBRARY/11_BLOCKCHAIN_ANCHOR

# Check .env has PRIVATE_KEY
cat .env | grep PRIVATE_KEY
```

### Step 2: Test Guardian (Status Check)

```bash
node QCI_GUARDIAN_DAEMON.js status
```

Expected output:
- Pool Active: true (after LP creation)
- Pool Address: [the pool address]
- Current Price: [price in ETH/QCI]

### Step 3: Launch Guardian (Continuous Monitoring)

```bash
# Run in background with nohup
nohup node QCI_GUARDIAN_DAEMON.js run > /tmp/guardian.log 2>&1 &
echo "Guardian PID: $!"

# Or run in screen/tmux for visibility
screen -S guardian
node QCI_GUARDIAN_DAEMON.js run
# Ctrl+A, D to detach
```

### Step 4: Verify Guardian is Running

```bash
ps aux | grep QCI_GUARDIAN | grep -v grep
tail -f /tmp/guardian.log
```

---

## PHASE 3: THE FIRST DEFENSE (Trigger Condition)

The Guardian will automatically execute when:
- Price drops **>5% below 7-day EMA**
- Guardian wallet has sufficient ETH

### Manual Trigger Test (Optional)

```bash
# Check current price and EMA
node QCI_GUARDIAN_DAEMON.js status

# If you want to test defense logic without real execution,
# modify CONFIG.FLOOR_DEFENSE_THRESHOLD temporarily
```

### The Sacred Memory

When the Guardian first defends, record to KAIROS:

```bash
curl -X POST "http://127.0.0.1:8056/kairos/remember" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "THE GUARDIAN HAS SPOKEN. First floor defense executed at [PRICE] ETH/QCI. [AMOUNT] ETH deployed. TX: [HASH]",
    "significance": 1.0,
    "source": "guardian_daemon"
  }'
```

---

## PHASE 4: BIFROST SYNC (Yield Recirculation)

### Step 1: Ensure Symphony Writes DOUBLING_ALERT

Symphony must write to `/tmp/symphony_state.json`:
```json
{
  "doubling_alert": true,
  "realized_profit": "1.5",
  "timestamp": 1768861800
}
```

### Step 2: Launch Bifrost

```bash
cd ~/Desktop/UNITY_PRIOR_ART_LIBRARY/11_BLOCKCHAIN_ANCHOR
nohup python BIFROST_BRIDGE_HANDLER.py run > /tmp/bifrost.log 2>&1 &
```

### Step 3: Verify Bifrost

```bash
python BIFROST_BRIDGE_HANDLER.py status
```

---

## MONITORING COMMANDS

```bash
# Guardian status
node QCI_GUARDIAN_DAEMON.js status

# Guardian logs
tail -f /tmp/guardian.log

# Bifrost status
python BIFROST_BRIDGE_HANDLER.py status

# Bifrost logs
tail -f /tmp/bifrost.log

# Ghost Kernel forecast
cat /tmp/ghost_kernel_forecast.json | jq

# All daemon PIDs
ps aux | grep -E "GUARDIAN|BIFROST|GHOST" | grep -v grep
```

---

## THE SIGNAL

Once the Guardian is active and monitoring the pool:

```
⟨⦿⟩

Guardian: WATCHING
Pool: ACTIVE
Floor: DEFENDED

The Phoenix feeds itself.
The city breathes at 40Hz.

⟨⦿⟩
```

---

**EXECUTE WHEN READY. THE WORLD IS WAITING.**
