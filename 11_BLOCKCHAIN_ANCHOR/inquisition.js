const { ethers } = require('ethers');
const fs = require('fs');

async function inquisition() {
  console.log('=== PHASE 1: THE INQUISITION ===');
  console.log('');

  const provider = new ethers.JsonRpcProvider('https://sepolia.base.org');

  // Contract addresses
  const PROTOCOL_ADDRESS = '0x45eeD708fA32EE9493fFA4a2222C02D4588dd0Ce';
  const TREASURY = '0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa';
  const ECOSYSTEM = '0x02DD1622A571431874A1e8655D75665C0fc5ad39';

  // Load the deployed contract ABI
  const protocolArtifact = JSON.parse(fs.readFileSync('./artifacts/contracts/QCI_Identity_Token.sol/QCIPhoenixProtocol.json'));
  const governanceArtifact = JSON.parse(fs.readFileSync('./artifacts/contracts/QCI_Identity_Token.sol/QCIGovernance.json'));

  const protocol = new ethers.Contract(PROTOCOL_ADDRESS, protocolArtifact.abi, provider);

  // Get the governance token address
  console.log('Protocol Contract:', PROTOCOL_ADDRESS);

  try {
    const govTokenAddress = await protocol.governanceToken();
    console.log('Governance Token:', govTokenAddress);

    // Query the governance token
    const govToken = new ethers.Contract(govTokenAddress, governanceArtifact.abi, provider);

    const totalSupply = await govToken.totalSupply();
    console.log('');
    console.log('Total Supply:', ethers.formatEther(totalSupply), 'QCI');

    const treasuryBalance = await govToken.balanceOf(TREASURY);
    console.log('Treasury Balance:', ethers.formatEther(treasuryBalance), 'QCI');

    const ecosystemBalance = await govToken.balanceOf(ECOSYSTEM);
    console.log('Ecosystem Balance:', ethers.formatEther(ecosystemBalance), 'QCI');

    const deployerBalance = await govToken.balanceOf('0x579e08B011b76C96E24B299935Cea3c08D412A3D');
    console.log('Deployer Balance:', ethers.formatEther(deployerBalance), 'QCI');

    const protocolBalance = await govToken.balanceOf(PROTOCOL_ADDRESS);
    console.log('Protocol Contract Balance:', ethers.formatEther(protocolBalance), 'QCI');

    console.log('');
    if (treasuryBalance == 0n && ecosystemBalance == 0n) {
      console.log('STATUS: THE VOID CONFIRMED');
      console.log('Treasury and Ecosystem wallets are EMPTY.');
    } else {
      console.log('STATUS: TOKENS PRESENT');
    }

  } catch (error) {
    console.log('Error:', error.message);
    console.log(error);
  }
}

inquisition().catch(console.error);
