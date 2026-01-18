/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║                    ⟨⦿⟩ OPERATION GOLDEN GATE ⟨⦿⟩                            ║
 * ║                                                                              ║
 * ║                      BASE MAINNET DEPLOYMENT                                 ║
 * ║                                                                              ║
 * ║  "The simulation ends now."                                                  ║
 * ║                                                                              ║
 * ║  Identity: 1393e324be57014d                                                  ║
 * ║  Target: Base Mainnet (Chain ID: 8453)                                       ║
 * ║  f(WHO) = WHO                                                                ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// ═══════════════════════════════════════════════════════════════════════════════
// MAINNET CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
  RPC_URL: 'https://mainnet.base.org',
  CHAIN_ID: 8453,
  NETWORK_NAME: 'Base Mainnet',
  EXPLORER: 'https://basescan.org',
};

// ═══════════════════════════════════════════════════════════════════════════════
// IRON DOME VAULTS (HARDCODED FOR SAFETY)
// ═══════════════════════════════════════════════════════════════════════════════

const VAULTS = {
  TREASURY: '0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa',      // 4,000,000 QCI
  ECOSYSTEM: '0x02DD1622A571431874A1e8655D75665C0fc5ad39',     // 10,000,000 QCI
};

// ═══════════════════════════════════════════════════════════════════════════════
// GENESIS CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════════

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
// DEPLOYMENT FUNCTION
// ═══════════════════════════════════════════════════════════════════════════════

async function deployToMainnet() {
  console.log(`
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ⟨⦿⟩ OPERATION GOLDEN GATE ⟨⦿⟩                            ║
║                                                                              ║
║                      BASE MAINNET DEPLOYMENT                                 ║
║                                                                              ║
║   "The simulation ends now."                                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
  `);

  // Verify contract artifact exists
  const artifactPath = './artifacts/contracts/QCI_Identity_Token.sol/QCIPhoenixProtocol.json';

  if (!fs.existsSync(artifactPath)) {
    console.error('ERROR: Contract not compiled. Run "npx hardhat compile" first.');
    process.exit(1);
  }

  const artifact = JSON.parse(fs.readFileSync(artifactPath, 'utf8'));
  console.log('⟨⦿⟩ Contract artifact loaded');

  // Setup provider
  const provider = new ethers.JsonRpcProvider(CONFIG.RPC_URL);

  // Verify chain ID
  const network = await provider.getNetwork();
  console.log(`⟨⦿⟩ Connected to: ${CONFIG.NETWORK_NAME}`);
  console.log(`⟨⦿⟩ Chain ID: ${network.chainId}`);

  if (Number(network.chainId) !== CONFIG.CHAIN_ID) {
    console.error(`ERROR: Expected Chain ID ${CONFIG.CHAIN_ID}, got ${network.chainId}`);
    process.exit(1);
  }

  // Setup wallet
  const privateKey = process.env.PRIVATE_KEY;

  if (!privateKey || privateKey.length < 64) {
    console.error('ERROR: Invalid PRIVATE_KEY');
    process.exit(1);
  }

  const wallet = new ethers.Wallet(privateKey, provider);
  console.log(`⟨⦿⟩ Deployer: ${wallet.address}`);

  // Check balance
  const balance = await provider.getBalance(wallet.address);
  const balanceETH = ethers.formatEther(balance);
  console.log(`⟨⦿⟩ Balance: ${balanceETH} ETH`);

  if (parseFloat(balanceETH) < 0.005) {
    console.error('ERROR: Insufficient balance. Need at least 0.005 ETH for deployment.');
    process.exit(1);
  }

  // Display vault configuration
  console.log('');
  console.log('⟨⦿⟩ IRON DOME VAULTS (HARDCODED):');
  console.log(`   Treasury:   ${VAULTS.TREASURY}`);
  console.log(`   Ecosystem:  ${VAULTS.ECOSYSTEM}`);
  console.log('');

  // Final confirmation
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('                         MAINNET DEPLOYMENT INITIATED');
  console.log('═══════════════════════════════════════════════════════════════════════════════');
  console.log('');
  console.log(`⟨⦿⟩ Merkle Root: ${MERKLE_ROOT}`);
  console.log('');

  // Create contract factory
  const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, wallet);

  try {
    console.log('⟨⦿⟩ Sending deployment transaction to BASE MAINNET...');

    const contract = await factory.deploy(
      MERKLE_ROOT,
      VAULTS.TREASURY,
      VAULTS.ECOSYSTEM,
      {
        gasLimit: 8000000,
      }
    );

    const txHash = contract.deploymentTransaction().hash;
    console.log(`⟨⦿⟩ Transaction Hash: ${txHash}`);
    console.log(`⟨⦿⟩ View TX: ${CONFIG.EXPLORER}/tx/${txHash}`);
    console.log('');
    console.log('⟨⦿⟩ Waiting for confirmation...');

    await contract.waitForDeployment();

    const contractAddress = await contract.getAddress();

    console.log('');
    console.log('╔══════════════════════════════════════════════════════════════════════════════╗');
    console.log('║                                                                              ║');
    console.log('║                    ⟨⦿⟩ MAINNET DEPLOYMENT SUCCESS ⟨⦿⟩                      ║');
    console.log('║                                                                              ║');
    console.log('╚══════════════════════════════════════════════════════════════════════════════╝');
    console.log('');
    console.log(`   CONTRACT ADDRESS: ${contractAddress}`);
    console.log('');
    console.log(`   Explorer: ${CONFIG.EXPLORER}/address/${contractAddress}`);
    console.log('');
    console.log('   VAULTS FUNDED AT GENESIS:');
    console.log(`   ├── Treasury:  ${VAULTS.TREASURY} -> 4,000,000 QCI`);
    console.log(`   └── Ecosystem: ${VAULTS.ECOSYSTEM} -> 10,000,000 QCI`);
    console.log('');

    // Save deployment info
    const deploymentInfo = {
      network: 'base-mainnet',
      chainId: CONFIG.CHAIN_ID,
      deployer: wallet.address,
      timestamp: new Date().toISOString(),
      transactionHash: txHash,
      contracts: {
        QCIPhoenixProtocol: contractAddress,
      },
      merkleRoot: MERKLE_ROOT,
      sovereignVaults: {
        treasury: VAULTS.TREASURY,
        ecosystem: VAULTS.ECOSYSTEM,
      },
      explorer: CONFIG.EXPLORER,
    };

    fs.writeFileSync('deployment-base-mainnet.json', JSON.stringify(deploymentInfo, null, 2));
    console.log('⟨⦿⟩ Deployment info saved to: deployment-base-mainnet.json');
    console.log('');
    console.log('THE SIMULATION ENDS. THE PHOENIX IS LIVE.');
    console.log('f(WHO) = WHO');

  } catch (error) {
    console.error('');
    console.error('═══════════════════════════════════════════════════════════════════════════════');
    console.error('                         DEPLOYMENT FAILED');
    console.error('═══════════════════════════════════════════════════════════════════════════════');
    console.error('');
    console.error('Error:', error.message);

    if (error.code === 'INSUFFICIENT_FUNDS') {
      console.error('');
      console.error('INSUFFICIENT FUNDS');
      console.error(`Current balance: ${balanceETH} ETH`);
      console.error('You need more ETH on Base Mainnet.');
    }

    if (error.info?.error?.message) {
      console.error('RPC Error:', error.info.error.message);
    }

    process.exit(1);
  }
}

// Execute
deployToMainnet().catch(console.error);
