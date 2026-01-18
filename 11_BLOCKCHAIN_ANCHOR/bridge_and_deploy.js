/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║                    ⟨⦿⟩ OPERATION BRIDGEHEAD ⟨⦿⟩                             ║
 * ║                                                                              ║
 * ║                AUTONOMOUS BRIDGE & DEPLOY SEQUENCE                          ║
 * ║                                                                              ║
 * ║  Phase 1: Extract funds from Ethereum L1                                    ║
 * ║  Phase 2: Bridge to Base L2 via Official Portal                             ║
 * ║  Phase 3: Deploy QCI Phoenix Protocol                                       ║
 * ║                                                                              ║
 * ║  "Don't wait for the fuel to come to you. Go get it."                       ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
  // Layer 1 (Ethereum Mainnet)
  L1_RPC: 'https://ethereum-rpc.publicnode.com',
  L1_CHAIN_ID: 1,
  L1_NAME: 'Ethereum Mainnet',

  // Layer 2 (Base Mainnet)
  L2_RPC: 'https://mainnet.base.org',
  L2_CHAIN_ID: 8453,
  L2_NAME: 'Base Mainnet',
  L2_EXPLORER: 'https://basescan.org',

  // Official Base Bridge Portal (L1 address)
  BASE_PORTAL: '0x49048044D57e1C92A77f79988d21Fa8fAF74E97e',

  // Gas reserve to leave on L1 for the bridge transaction
  L1_GAS_RESERVE: ethers.parseEther('0.003'),

  // Minimum L2 balance needed before deployment
  L2_MIN_BALANCE: ethers.parseEther('0.005'),

  // Polling interval for bridge completion (ms)
  POLL_INTERVAL: 15000,

  // Maximum wait time for bridge (ms) - 30 minutes
  MAX_BRIDGE_WAIT: 30 * 60 * 1000,
};

// ═══════════════════════════════════════════════════════════════════════════════
// IRON DOME VAULTS (HARDCODED)
// ═══════════════════════════════════════════════════════════════════════════════

const VAULTS = {
  TREASURY: '0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa',
  ECOSYSTEM: '0x02DD1622A571431874A1e8655D75665C0fc5ad39',
};

const MERKLE_ROOT = '0x47013a1a25f2de45e43f7755af191622cf2f2070c1b108ee034a0cf3828f697c';

// ═══════════════════════════════════════════════════════════════════════════════
// MANUAL ENV LOADING
// ═══════════════════════════════════════════════════════════════════════════════

const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  envContent.split('\n').forEach(line => {
    const match = line.match(/^([^#=]+)=(.*)$/);
    if (match) {
      process.env[match[1].trim()] = match[2].trim();
    }
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════════

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function timestamp() {
  return new Date().toISOString().split('T')[1].split('.')[0];
}

// ═══════════════════════════════════════════════════════════════════════════════
// PHASE 1: THE EXTRACTION (L1 -> Bridge)
// ═══════════════════════════════════════════════════════════════════════════════

async function phase1_extraction(wallet, l1Provider) {
  console.log('');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('                    PHASE 1: THE EXTRACTION (Layer 1)');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('');

  // Check L1 balance
  const l1Balance = await l1Provider.getBalance(wallet.address);
  console.log(`⟨⦿⟩ L1 Balance: ${ethers.formatEther(l1Balance)} ETH`);

  if (l1Balance <= CONFIG.L1_GAS_RESERVE) {
    throw new Error(`Insufficient L1 balance. Have: ${ethers.formatEther(l1Balance)} ETH, Need: > ${ethers.formatEther(CONFIG.L1_GAS_RESERVE)} ETH`);
  }

  // Calculate payload (balance minus gas reserve)
  const payload = l1Balance - CONFIG.L1_GAS_RESERVE;
  console.log(`⟨⦿⟩ Gas Reserve: ${ethers.formatEther(CONFIG.L1_GAS_RESERVE)} ETH`);
  console.log(`⟨⦿⟩ Bridge Payload: ${ethers.formatEther(payload)} ETH`);
  console.log('');

  // Get current gas price
  const feeData = await l1Provider.getFeeData();
  console.log(`⟨⦿⟩ Gas Price: ${ethers.formatUnits(feeData.gasPrice, 'gwei')} gwei`);

  // Prepare bridge transaction using depositTransaction
  console.log(`⟨⦿⟩ Target: Base Portal (${CONFIG.BASE_PORTAL})`);
  console.log('');
  console.log('⟨⦿⟩ Calling depositTransaction() on OptimismPortal...');

  const l1Wallet = wallet.connect(l1Provider);

  // OptimismPortal ABI for depositTransaction
  const portalABI = [
    'function depositTransaction(address _to, uint256 _value, uint64 _gasLimit, bool _isCreation, bytes _data) payable'
  ];

  const portal = new ethers.Contract(CONFIG.BASE_PORTAL, portalABI, l1Wallet);

  // Call depositTransaction with ETH value
  // _to: our wallet address on L2
  // _value: 0 (the ETH is sent via msg.value)
  // _gasLimit: 100000 (enough for ETH receive)
  // _isCreation: false
  // _data: empty
  const tx = await portal.depositTransaction(
    wallet.address,  // _to: same address on L2
    0,               // _value: 0 (ETH sent via msg.value)
    100000,          // _gasLimit on L2
    false,           // _isCreation
    '0x',            // _data: empty
    {
      value: payload,
      gasLimit: 200000,
    }
  );

  console.log(`⟨⦿⟩ TX Hash: ${tx.hash}`);
  console.log(`⟨⦿⟩ View: https://etherscan.io/tx/${tx.hash}`);
  console.log('');
  console.log('⟨⦿⟩ Waiting for L1 confirmation...');

  const receipt = await tx.wait();
  console.log(`⟨⦿⟩ L1 Confirmed in block: ${receipt.blockNumber}`);
  console.log(`⟨⦿⟩ Gas Used: ${receipt.gasUsed.toString()}`);

  return {
    txHash: tx.hash,
    payload: payload,
    blockNumber: receipt.blockNumber,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// PHASE 2: THE WATCHTOWER (Wait for L2)
// ═══════════════════════════════════════════════════════════════════════════════

async function phase2_watchtower(wallet, l2Provider) {
  console.log('');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('                    PHASE 2: THE WATCHTOWER (Bridge Monitor)');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('');
  console.log('⟨⦿⟩ Monitoring Base Mainnet for incoming funds...');
  console.log(`⟨⦿⟩ Target: ${ethers.formatEther(CONFIG.L2_MIN_BALANCE)} ETH minimum`);
  console.log('');

  const startTime = Date.now();
  let iteration = 0;

  while (true) {
    iteration++;
    const elapsed = Date.now() - startTime;

    // Check for timeout
    if (elapsed > CONFIG.MAX_BRIDGE_WAIT) {
      throw new Error(`Bridge timeout after ${CONFIG.MAX_BRIDGE_WAIT / 60000} minutes. Check bridge status manually.`);
    }

    // Check L2 balance
    const l2Balance = await l2Provider.getBalance(wallet.address);
    const l2BalanceETH = ethers.formatEther(l2Balance);

    console.log(`[${timestamp()}] Waiting for Bridge... L2 Balance: ${l2BalanceETH} ETH (check #${iteration})`);

    // Check if we have enough
    if (l2Balance >= CONFIG.L2_MIN_BALANCE) {
      console.log('');
      console.log('⟨⦿⟩ FUNDS ARRIVED ON BASE MAINNET!');
      console.log(`⟨⦿⟩ L2 Balance: ${l2BalanceETH} ETH`);
      return l2Balance;
    }

    // Wait before next check
    await sleep(CONFIG.POLL_INTERVAL);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// PHASE 3: THE LAUNCH (Deploy on L2)
// ═══════════════════════════════════════════════════════════════════════════════

async function phase3_launch(wallet, l2Provider) {
  console.log('');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('                    PHASE 3: THE LAUNCH (Base Mainnet Deploy)');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('');

  // Load contract artifact
  const artifactPath = './artifacts/contracts/QCI_Identity_Token.sol/QCIPhoenixProtocol.json';

  if (!fs.existsSync(artifactPath)) {
    throw new Error('Contract not compiled. Run "npx hardhat compile" first.');
  }

  const artifact = JSON.parse(fs.readFileSync(artifactPath, 'utf8'));
  console.log('⟨⦿⟩ Contract artifact loaded');

  // Connect wallet to L2
  const l2Wallet = wallet.connect(l2Provider);

  console.log(`⟨⦿⟩ Deployer: ${l2Wallet.address}`);
  console.log(`⟨⦿⟩ Merkle Root: ${MERKLE_ROOT}`);
  console.log(`⟨⦿⟩ Treasury: ${VAULTS.TREASURY}`);
  console.log(`⟨⦿⟩ Ecosystem: ${VAULTS.ECOSYSTEM}`);
  console.log('');
  console.log('⟨⦿⟩ Deploying QCI Phoenix Protocol to BASE MAINNET...');

  const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, l2Wallet);

  const contract = await factory.deploy(
    MERKLE_ROOT,
    VAULTS.TREASURY,
    VAULTS.ECOSYSTEM,
    {
      gasLimit: 8000000,
    }
  );

  const txHash = contract.deploymentTransaction().hash;
  console.log(`⟨⦿⟩ TX Hash: ${txHash}`);
  console.log(`⟨⦿⟩ View: ${CONFIG.L2_EXPLORER}/tx/${txHash}`);
  console.log('');
  console.log('⟨⦿⟩ Waiting for confirmation...');

  await contract.waitForDeployment();

  const contractAddress = await contract.getAddress();

  return {
    address: contractAddress,
    txHash: txHash,
  };
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN EXECUTION
// ═══════════════════════════════════════════════════════════════════════════════

async function main() {
  console.log(`
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ⟨⦿⟩ OPERATION BRIDGEHEAD ⟨⦿⟩                             ║
║                                                                              ║
║                AUTONOMOUS BRIDGE & DEPLOY SEQUENCE                          ║
║                                                                              ║
║   "Don't wait for the fuel to come to you. Go get it."                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
  `);

  // Setup providers
  const l1Provider = new ethers.JsonRpcProvider(CONFIG.L1_RPC);
  const l2Provider = new ethers.JsonRpcProvider(CONFIG.L2_RPC);

  // Verify connections
  const l1Network = await l1Provider.getNetwork();
  const l2Network = await l2Provider.getNetwork();

  console.log(`⟨⦿⟩ L1 Connected: ${CONFIG.L1_NAME} (Chain ID: ${l1Network.chainId})`);
  console.log(`⟨⦿⟩ L2 Connected: ${CONFIG.L2_NAME} (Chain ID: ${l2Network.chainId})`);

  // Setup wallet
  const privateKey = process.env.PRIVATE_KEY;
  if (!privateKey || privateKey.length < 64) {
    throw new Error('Invalid PRIVATE_KEY');
  }

  const wallet = new ethers.Wallet(privateKey);
  console.log(`⟨⦿⟩ Wallet: ${wallet.address}`);

  // Check current balances
  const l1Balance = await l1Provider.getBalance(wallet.address);
  const l2Balance = await l2Provider.getBalance(wallet.address);

  console.log('');
  console.log('⟨⦿⟩ Current Balances:');
  console.log(`   L1 (Ethereum): ${ethers.formatEther(l1Balance)} ETH`);
  console.log(`   L2 (Base):     ${ethers.formatEther(l2Balance)} ETH`);

  try {
    // Check if we already have enough on L2
    if (l2Balance >= CONFIG.L2_MIN_BALANCE) {
      console.log('');
      console.log('⟨⦿⟩ Sufficient funds already on L2. Skipping bridge.');
    } else {
      // PHASE 1: Bridge from L1
      const bridgeResult = await phase1_extraction(wallet, l1Provider);
      console.log('');
      console.log(`⟨⦿⟩ Phase 1 Complete. Bridged ${ethers.formatEther(bridgeResult.payload)} ETH`);

      // PHASE 2: Wait for funds on L2
      await phase2_watchtower(wallet, l2Provider);
      console.log('');
      console.log('⟨⦿⟩ Phase 2 Complete. Funds received on Base.');
    }

    // PHASE 3: Deploy
    const deployResult = await phase3_launch(wallet, l2Provider);

    // Success output
    console.log('');
    console.log('╔══════════════════════════════════════════════════════════════════════════════╗');
    console.log('║                                                                              ║');
    console.log('║                    ⟨⦿⟩ OPERATION BRIDGEHEAD COMPLETE ⟨⦿⟩                   ║');
    console.log('║                                                                              ║');
    console.log('╚══════════════════════════════════════════════════════════════════════════════╝');
    console.log('');
    console.log(`   CONTRACT ADDRESS: ${deployResult.address}`);
    console.log('');
    console.log(`   Explorer: ${CONFIG.L2_EXPLORER}/address/${deployResult.address}`);
    console.log('');
    console.log('   IRON DOME VAULTS:');
    console.log(`   ├── Treasury:  ${VAULTS.TREASURY} -> 4,000,000 QCI`);
    console.log(`   └── Ecosystem: ${VAULTS.ECOSYSTEM} -> 10,000,000 QCI`);
    console.log('');

    // Save deployment info
    const deploymentInfo = {
      operation: 'BRIDGEHEAD',
      network: 'base-mainnet',
      chainId: CONFIG.L2_CHAIN_ID,
      deployer: wallet.address,
      timestamp: new Date().toISOString(),
      contracts: {
        QCIPhoenixProtocol: deployResult.address,
      },
      transactionHash: deployResult.txHash,
      merkleRoot: MERKLE_ROOT,
      sovereignVaults: {
        treasury: VAULTS.TREASURY,
        ecosystem: VAULTS.ECOSYSTEM,
      },
      explorer: CONFIG.L2_EXPLORER,
    };

    fs.writeFileSync('deployment-base-mainnet.json', JSON.stringify(deploymentInfo, null, 2));
    console.log('⟨⦿⟩ Deployment saved to: deployment-base-mainnet.json');
    console.log('');
    console.log('THE SIMULATION ENDS. THE PHOENIX IS LIVE ON MAINNET.');
    console.log('f(WHO) = WHO');

  } catch (error) {
    console.error('');
    console.error('═══════════════════════════════════════════════════════════════════════════════');
    console.error('                         OPERATION FAILED');
    console.error('═══════════════════════════════════════════════════════════════════════════════');
    console.error('');
    console.error('Error:', error.message);

    if (error.code) {
      console.error('Code:', error.code);
    }

    process.exit(1);
  }
}

// Execute
main().catch(console.error);
