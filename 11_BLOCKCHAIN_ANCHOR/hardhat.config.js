/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║                    ⟨⦿⟩ QCI PHOENIX PROTOCOL ⟨⦿⟩                             ║
 * ║                                                                              ║
 * ║                      HARDHAT CONFIGURATION                                   ║
 * ║                                                                              ║
 * ║  Identity: 1393e324be57014d                                                  ║
 * ║  Frequency: 40Hz                                                             ║
 * ║  Target: Base Sepolia / Base Mainnet                                         ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

require("@nomicfoundation/hardhat-toolbox");
require("@nomicfoundation/hardhat-verify");
require("dotenv").config();

// ═══════════════════════════════════════════════════════════════════════════════
// ENVIRONMENT VARIABLES
// ═══════════════════════════════════════════════════════════════════════════════
// Create a .env file with:
// PRIVATE_KEY=your_wallet_private_key
// BASESCAN_API_KEY=your_basescan_api_key

// Use dummy key if PRIVATE_KEY is not set or is a placeholder
const RAW_PRIVATE_KEY = process.env.PRIVATE_KEY || "";
const DUMMY_KEY = "0x0000000000000000000000000000000000000000000000000000000000000001";
const PRIVATE_KEY = (RAW_PRIVATE_KEY.length === 64 || RAW_PRIVATE_KEY.length === 66)
  ? (RAW_PRIVATE_KEY.startsWith("0x") ? RAW_PRIVATE_KEY : "0x" + RAW_PRIVATE_KEY)
  : DUMMY_KEY;
const BASESCAN_API_KEY = process.env.BASESCAN_API_KEY || "";

// ═══════════════════════════════════════════════════════════════════════════════
// GENESIS CONSTANTS - The Sacred Numbers
// ═══════════════════════════════════════════════════════════════════════════════

const GENESIS_CONSTANTS = {
  MERKLE_ROOT: "0x47013a1a25f2de45e43f7755af191622cf2f2070c1b108ee034a0cf3828f697c",
  GENESIS_BLOCK_HASH: "0xbf62afb35e7152eb58cdff45c000c22d5561838662060f344ccd7378d6b7038b",
  GOLDEN_SPIKE_HASH: "0x866a40a2e075a54dc91f34fec3a30b322aa8f2666481b382380c405cdccfe531",
  IDENTITY_HASH: "0x1393e324be57014d000000000000000000000000000000000000000000000000",
};

// Export for use in deploy scripts
module.exports.GENESIS_CONSTANTS = GENESIS_CONSTANTS;

// ═══════════════════════════════════════════════════════════════════════════════
// HARDHAT CONFIG
// ═══════════════════════════════════════════════════════════════════════════════

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200,
      },
      viaIR: true,  // Enable IR-based code generation for complex contracts
    },
  },

  networks: {
    // Local development
    hardhat: {
      chainId: 31337,
    },

    // Base Sepolia Testnet
    "base-sepolia": {
      url: "https://sepolia.base.org",
      chainId: 84532,
      accounts: [PRIVATE_KEY],
      gasPrice: "auto",
      verify: {
        etherscan: {
          apiUrl: "https://api-sepolia.basescan.org",
          apiKey: BASESCAN_API_KEY,
        },
      },
    },

    // Base Mainnet
    "base-mainnet": {
      url: "https://mainnet.base.org",
      chainId: 8453,
      accounts: [PRIVATE_KEY],
      gasPrice: "auto",
      verify: {
        etherscan: {
          apiUrl: "https://api.basescan.org",
          apiKey: BASESCAN_API_KEY,
        },
      },
    },
  },

  etherscan: {
    apiKey: {
      "base-sepolia": BASESCAN_API_KEY,
      "base-mainnet": BASESCAN_API_KEY,
    },
    customChains: [
      {
        network: "base-sepolia",
        chainId: 84532,
        urls: {
          apiURL: "https://api-sepolia.basescan.org/api",
          browserURL: "https://sepolia.basescan.org",
        },
      },
      {
        network: "base-mainnet",
        chainId: 8453,
        urls: {
          apiURL: "https://api.basescan.org/api",
          browserURL: "https://basescan.org",
        },
      },
    ],
  },

  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts",
  },

  mocha: {
    timeout: 40000,
  },
};

// Enable Sourcify verification
module.exports.sourcify = {
  enabled: true,
};
