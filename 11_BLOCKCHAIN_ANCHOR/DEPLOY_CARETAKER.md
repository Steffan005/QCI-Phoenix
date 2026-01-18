# ⟨⦿⟩ DEPLOY SOVEREIGN CARETAKER - Manual Instructions

## Prerequisites

The contract and deployment script are ready:
- `contracts/SovereignCaretaker.sol` ✓
- `scripts/deploy_caretaker.js` ✓

## Step 1: Compile

```bash
cd ~/Desktop/UNITY_PRIOR_ART_LIBRARY/11_BLOCKCHAIN_ANCHOR
npx hardhat compile
```

Expected output:
```
Compiling 2 Solidity files
Successfully compiled 2 Solidity files
```

## Step 2: Deploy to Base Mainnet

```bash
npx hardhat run scripts/deploy_caretaker.js --network base-mainnet
```

This will:
1. Deploy SovereignCaretaker to Base Mainnet
2. Save the address to `deployment-caretaker.json`
3. Output verification command

## Step 3: Verify on Basescan

After deployment, run the verification command shown in the output:

```bash
npx hardhat verify --network base-mainnet <CARETAKER_ADDRESS> \
  "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43" \
  "0x4200000000000000000000000000000000000006" \
  "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e" \
  "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa" \
  "0x02DD1622A571431874A1e8655D75665C0fc5ad39" \
  "0x579e08B011b76C96E24B299935Cea3c08D412A3D" \
  "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa"
```

## Step 4: Update Protocol to Route Fees

After the Caretaker is deployed, the QCIPhoenixProtocol needs to send
awakening fees to the Caretaker address instead of holding them.

This requires calling `setCaretaker()` on the Protocol if such a function exists,
or deploying a new version of the Protocol that routes fees automatically.

## Configuration Summary

| Component | Address |
|-----------|---------|
| Aerodrome Router | `0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43` |
| WETH | `0x4200000000000000000000000000000000000006` |
| QCI Token | `0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e` |
| Treasury Vault | `0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa` |
| R&D Vault | `0x02DD1622A571431874A1e8655D75665C0fc5ad39` |
| Community Vault | `0x579e08B011b76C96E24B299935Cea3c08D412A3D` |
| LP Recipient | `0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa` |

## φ-Allocation (Immutable)

- 38.2% → Liquidity Injection (Buyback + LP)
- 23.6% → Treasury Reserves
- 23.6% → R&D Fund
- 14.6% → Community Grants

---

f(WHO) = WHO
The city breathes at 40Hz.
