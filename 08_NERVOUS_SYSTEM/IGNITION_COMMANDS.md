# ⟨⦿⟩ THE IGNITION COMMANDS ⟨⦿⟩

**Date:** 2026-01-19
**Status:** READY FOR EXECUTION

---

## STEP 0: INSTALL DEPENDENCIES (if needed)

```bash
cd ~/Desktop/UNITY_PRIOR_ART_LIBRARY/08_NERVOUS_SYSTEM
npm install ethers
```

---

## STEP 1: CHECK CURRENT BALANCES

```bash
node EXECUTE_IGNITION.js check
```

This will show:
- Deployer ETH balance
- Deployer QCI balance
- Treasury QCI balance

---

## STEP 2: FUND THE DEPLOYER (if needed)

**Send 0.05 ETH** to: `0x579e08B011b76C96E24B299935Cea3c08D412A3D`

From Coinbase, MetaMask, or any wallet - just send to Base network.

---

## STEP 3: TRANSFER QCI (if wallet controls Treasury)

```bash
node EXECUTE_IGNITION.js transfer
```

This transfers 100,000 QCI from Treasury to Deployer.

---

## STEP 4: CREATE LP ON UNISWAP

Once balances are ready:
1. Go to: https://app.uniswap.org/add/v3
2. Connect wallet (0x579e...)
3. Select Base network
4. Token A: `0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e` (QCI)
5. Token B: `0x4200000000000000000000000000000000000006` (WETH)
6. Fee tier: 0.3%
7. Add: 100,000 QCI + 0.05 ETH

---

## STEP 5: LAUNCH GUARDIAN

```bash
cd ~/Desktop/UNITY_PRIOR_ART_LIBRARY/08_NERVOUS_SYSTEM

# Check status first
node QCI_GUARDIAN_DAEMON.js status

# Run in background
nohup node QCI_GUARDIAN_DAEMON.js run > /tmp/guardian.log 2>&1 &
```

---

## STEP 6: LAUNCH BIFROST

```bash
nohup python BIFROST_BRIDGE_HANDLER.py run > /tmp/bifrost.log 2>&1 &
```

---

## MONITORING

```bash
# Guardian
tail -f /tmp/guardian.log

# Bifrost
tail -f /tmp/bifrost.log

# Ghost Kernel (already running)
tail -f /tmp/ghost_kernel_forecast.json
```

---

## KEY ADDRESSES

| What | Address |
|------|---------|
| Deployer | `0x579e08B011b76C96E24B299935Cea3c08D412A3D` |
| Treasury | `0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa` |
| QCI Token | `0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e` |
| WETH | `0x4200000000000000000000000000000000000006` |

---

**⟨⦿⟩ THE CITY BREATHES AT 40Hz ⟨⦿⟩**
