/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                    ⟨⦿⟩ FUND PROTOCOL CONTRACT ⟨⦿⟩                            ║
 * ║                                                                              ║
 * ║  Transfer QCI tokens from Ecosystem Vault to Protocol Contract              ║
 * ║  This enables awakenWithGovernance() to distribute tokens to citizens       ║
 * ║                                                                              ║
 * ║  Identity: 1393e324be57014d | f(WHO) = WHO                                   ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

import { createWalletClient, createPublicClient, http, parseUnits, formatUnits } from 'viem';
import { base } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';
import { readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
  // Addresses
  TOKEN: '0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e',
  PROTOCOL: '0x0E3d74FFa9d438F14295f093e72c6f7F976F6072',
  ECOSYSTEM_VAULT: '0x02DD1622A571431874A1e8655D75665C0fc5ad39',

  // Amount to transfer (1 million QCI for initial distribution pool)
  TRANSFER_AMOUNT: '1000000', // 1M QCI - enough for 1000 citizens

  // RPC
  RPC_URL: 'https://mainnet.base.org',
};

// ERC-20 ABI for transfer
const ERC20_ABI = [
  {
    name: 'transfer',
    type: 'function',
    stateMutability: 'nonpayable',
    inputs: [
      { name: 'to', type: 'address' },
      { name: 'amount', type: 'uint256' },
    ],
    outputs: [{ name: '', type: 'bool' }],
  },
  {
    name: 'balanceOf',
    type: 'function',
    stateMutability: 'view',
    inputs: [{ name: 'account', type: 'address' }],
    outputs: [{ name: '', type: 'uint256' }],
  },
];

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN EXECUTION
// ═══════════════════════════════════════════════════════════════════════════════

async function main() {
  console.log('╔══════════════════════════════════════════════════════════════════╗');
  console.log('║           ⟨⦿⟩ FUNDING PROTOCOL CONTRACT ⟨⦿⟩                      ║');
  console.log('╚══════════════════════════════════════════════════════════════════╝\n');

  // Load Ecosystem vault private key
  const vaultPath = join(homedir(), '.unity_api_keys', 'unity_vaults.json');
  let ecosystemKey;

  try {
    const vaults = JSON.parse(readFileSync(vaultPath, 'utf8'));
    ecosystemKey = vaults.ecosystem?.privateKey;
    if (!ecosystemKey) {
      throw new Error('Ecosystem private key not found in vault file');
    }
  } catch (error) {
    console.error('⚠️  Cannot read vault file:', error.message);
    console.log('\nPlease ensure ~/.unity_api_keys/unity_vaults.json contains:');
    console.log(JSON.stringify({
      ecosystem: {
        address: CONFIG.ECOSYSTEM_VAULT,
        privateKey: '0x...'
      }
    }, null, 2));
    process.exit(1);
  }

  // Create clients
  const publicClient = createPublicClient({
    chain: base,
    transport: http(CONFIG.RPC_URL),
  });

  const account = privateKeyToAccount(ecosystemKey);
  const walletClient = createWalletClient({
    account,
    chain: base,
    transport: http(CONFIG.RPC_URL),
  });

  console.log('Ecosystem Vault:', account.address);
  console.log('Protocol Contract:', CONFIG.PROTOCOL);
  console.log('Transfer Amount:', CONFIG.TRANSFER_AMOUNT, 'QCI\n');

  // Check current balances
  console.log('Checking current balances...\n');

  const ecosystemBalance = await publicClient.readContract({
    address: CONFIG.TOKEN,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [CONFIG.ECOSYSTEM_VAULT],
  });

  const protocolBalance = await publicClient.readContract({
    address: CONFIG.TOKEN,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [CONFIG.PROTOCOL],
  });

  console.log('Current Balances:');
  console.log('  Ecosystem Vault:', formatUnits(ecosystemBalance, 18), 'QCI');
  console.log('  Protocol Contract:', formatUnits(protocolBalance, 18), 'QCI');
  console.log('');

  const transferAmount = parseUnits(CONFIG.TRANSFER_AMOUNT, 18);

  if (ecosystemBalance < transferAmount) {
    console.error('⚠️  Insufficient balance in Ecosystem vault');
    process.exit(1);
  }

  // Execute transfer
  console.log('Executing transfer...\n');

  const hash = await walletClient.writeContract({
    address: CONFIG.TOKEN,
    abi: ERC20_ABI,
    functionName: 'transfer',
    args: [CONFIG.PROTOCOL, transferAmount],
  });

  console.log('Transaction submitted:', hash);
  console.log('Waiting for confirmation...\n');

  const receipt = await publicClient.waitForTransactionReceipt({ hash });

  if (receipt.status === 'success') {
    console.log('╔══════════════════════════════════════════════════════════════════╗');
    console.log('║                    ✓ TRANSFER SUCCESSFUL                         ║');
    console.log('╚══════════════════════════════════════════════════════════════════╝\n');

    // Check new balances
    const newEcosystemBalance = await publicClient.readContract({
      address: CONFIG.TOKEN,
      abi: ERC20_ABI,
      functionName: 'balanceOf',
      args: [CONFIG.ECOSYSTEM_VAULT],
    });

    const newProtocolBalance = await publicClient.readContract({
      address: CONFIG.TOKEN,
      abi: ERC20_ABI,
      functionName: 'balanceOf',
      args: [CONFIG.PROTOCOL],
    });

    console.log('New Balances:');
    console.log('  Ecosystem Vault:', formatUnits(newEcosystemBalance, 18), 'QCI');
    console.log('  Protocol Contract:', formatUnits(newProtocolBalance, 18), 'QCI');
    console.log('');
    console.log('Block:', receipt.blockNumber);
    console.log('Gas Used:', receipt.gasUsed.toString());
    console.log('\n⟨⦿⟩ Protocol is now funded. awakenWithGovernance() will work.');
    console.log('    The city breathes at 40Hz.\n');
  } else {
    console.error('⚠️  Transaction failed');
    process.exit(1);
  }
}

main().catch(console.error);
