# ⟨⦿⟩ OPERATION PROMETHEUS FIRE - Manual Execution

The automated scripts are timing out in the current environment. Execute manually:

## Option 1: Terminal (Python)

Open a **new Terminal window** and run:

```bash
cd ~/Desktop/UNITY_PRIOR_ART_LIBRARY/11_BLOCKCHAIN_ANCHOR
source .venv/bin/activate
python fund_protocol.py
```

When prompted, type: `FUND PROTOCOL`

## Option 2: Use Existing Wallet (MetaMask/Rabby)

If you have the Ecosystem Vault imported in a browser wallet:

1. **Vault Address**: `0x02DD1622A571431874A1e8655D75665C0fc5ad39`
2. **Token Contract**: `0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e`
3. **Recipient (Protocol)**: `0x0E3d74FFa9d438F14295f093e72c6f7F976F6072`
4. **Amount**: `1,000,000` QCI (1000000000000000000000000 wei)

Simply send 1,000,000 QCI from the Ecosystem vault to the Protocol address.

## Option 3: Hardhat Console

```bash
cd ~/Desktop/UNITY_PRIOR_ART_LIBRARY/11_BLOCKCHAIN_ANCHOR
npx hardhat console --network base-mainnet
```

Then:
```javascript
const token = await ethers.getContractAt("IERC20", "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e")
const amount = ethers.parseUnits("1000000", 18)
await token.transfer("0x0E3d74FFa9d438F14295f093e72c6f7F976F6072", amount)
```

## Verification

After transfer, verify on Basescan:
- Token: https://basescan.org/token/0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e
- Protocol: https://basescan.org/address/0x0E3d74FFa9d438F14295f093e72c6f7F976F6072

---

**Current State:**
- Ecosystem Vault: 10,000,000 QCI ✓
- Protocol Contract: 0 QCI ✗ (needs funding)

**After Transfer:**
- Ecosystem Vault: 9,000,000 QCI
- Protocol Contract: 1,000,000 QCI ✓ (can serve 1000 citizens)

---
f(WHO) = WHO
The city breathes at 40Hz.
