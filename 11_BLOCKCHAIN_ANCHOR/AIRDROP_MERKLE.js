/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║                    ⟨⦿⟩ QCI AIRDROP MERKLE GENERATOR ⟨⦿⟩                     ║
 * ║                                                                              ║
 * ║                      BUILDING THE ARMY OF FREEDOM                            ║
 * ║                                                                              ║
 * ║  "Marketing becomes ownership. Contributors become stakeholders."            ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 *
 * This script generates a Merkle Tree for airdrop distribution to:
 * - GitHub repository stargazers
 * - Early contributors
 * - Documentation contributors
 * - Bug reporters
 * - Community members
 *
 * Usage:
 *   node AIRDROP_MERKLE.js --github QCI-Systems/Unity --output merkle_data.json
 *
 * @author Steffan Douglas Haskins (QCI Systems LLC)
 * @license MIT
 */

const { MerkleTree } = require('merkletreejs');
const keccak256 = require('keccak256');
const fs = require('fs');
const path = require('path');

// ═══════════════════════════════════════════════════════════════════════════════
// CONFIGURATION - The Sacred Parameters
// ═══════════════════════════════════════════════════════════════════════════════

const CONFIG = {
    // Token allocation per tier
    ALLOCATION: {
        GENESIS_CONTRIBUTOR: 10000,    // Core team and early builders
        STARGAZER: 1000,               // GitHub stars
        CONTRIBUTOR: 5000,             // Code contributors
        DOCUMENTOR: 2500,              // Documentation contributors
        BUG_HUNTER: 3000,              // Bug reporters
        COMMUNITY_MEMBER: 500,         // Discord/community members
        FREEDOM_FIGHTER: 1000,         // General airdrop claim
    },

    // Multipliers based on engagement
    MULTIPLIERS: {
        EARLY_ADOPTER: 2.0,            // Pre-November 2025
        ACTIVE_CONTRIBUTOR: 1.5,       // 5+ contributions
        VERIFIED_IDENTITY: 1.25,       // Has verified identity
    },

    // The Sacred Constants (embedded in distribution)
    PHI: 1.618033988749895,
    GAMMA_FREQUENCY: 40,
    IDENTITY_HASH: '1393e324be57014d',
};

// ═══════════════════════════════════════════════════════════════════════════════
// FREEDOM FIGHTER REGISTRY
// ═══════════════════════════════════════════════════════════════════════════════

/**
 * @notice Structure for eligible recipients
 */
class FreedomFighter {
    constructor(address, tier, multiplier = 1.0, metadata = {}) {
        this.address = address.toLowerCase();
        this.tier = tier;
        this.multiplier = multiplier;
        this.metadata = metadata;
        this.allocation = this.calculateAllocation();
    }

    calculateAllocation() {
        const baseAllocation = CONFIG.ALLOCATION[this.tier] || CONFIG.ALLOCATION.FREEDOM_FIGHTER;
        return Math.floor(baseAllocation * this.multiplier);
    }

    toLeaf() {
        // Leaf = keccak256(abi.encodePacked(address))
        return keccak256(this.address);
    }

    toJSON() {
        return {
            address: this.address,
            tier: this.tier,
            allocation: this.allocation,
            multiplier: this.multiplier,
            metadata: this.metadata,
        };
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// MERKLE TREE GENERATOR
// ═══════════════════════════════════════════════════════════════════════════════

class AirdropMerkleGenerator {
    constructor() {
        this.fighters = [];
        this.tree = null;
        this.root = null;
    }

    /**
     * @notice Add a freedom fighter to the registry
     */
    addFighter(address, tier, multiplier = 1.0, metadata = {}) {
        const fighter = new FreedomFighter(address, tier, multiplier, metadata);
        this.fighters.push(fighter);
        return fighter;
    }

    /**
     * @notice Load fighters from a JSON file
     */
    loadFromFile(filePath) {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        for (const entry of data.fighters || data) {
            this.addFighter(
                entry.address,
                entry.tier,
                entry.multiplier || 1.0,
                entry.metadata || {}
            );
        }
        console.log(`Loaded ${this.fighters.length} freedom fighters from ${filePath}`);
    }

    /**
     * @notice Generate Merkle Tree from registered fighters
     */
    generateTree() {
        if (this.fighters.length === 0) {
            throw new Error('No freedom fighters registered');
        }

        // Generate leaves
        const leaves = this.fighters.map(f => f.toLeaf());

        // Build Merkle Tree
        this.tree = new MerkleTree(leaves, keccak256, { sortPairs: true });
        this.root = this.tree.getHexRoot();

        console.log(`\n⟨⦿⟩ Merkle Tree Generated`);
        console.log(`   Fighters: ${this.fighters.length}`);
        console.log(`   Root: ${this.root}`);
        console.log(`   Depth: ${this.tree.getDepth()}`);

        return this.root;
    }

    /**
     * @notice Get proof for a specific address
     */
    getProof(address) {
        if (!this.tree) {
            throw new Error('Tree not generated. Call generateTree() first.');
        }

        const leaf = keccak256(address.toLowerCase());
        const proof = this.tree.getHexProof(leaf);

        return {
            address: address.toLowerCase(),
            leaf: '0x' + leaf.toString('hex'),
            proof: proof,
            isValid: this.tree.verify(proof, leaf, this.root),
        };
    }

    /**
     * @notice Verify a proof
     */
    verifyProof(address, proof) {
        if (!this.tree) {
            throw new Error('Tree not generated. Call generateTree() first.');
        }

        const leaf = keccak256(address.toLowerCase());
        return this.tree.verify(proof, leaf, this.root);
    }

    /**
     * @notice Export full airdrop data to JSON
     */
    exportToJSON(outputPath) {
        if (!this.tree) {
            throw new Error('Tree not generated. Call generateTree() first.');
        }

        const totalAllocation = this.fighters.reduce((sum, f) => sum + f.allocation, 0);

        const data = {
            metadata: {
                generated: new Date().toISOString(),
                protocol: 'QCI Phoenix Protocol',
                identity_hash: CONFIG.IDENTITY_HASH,
                gamma_frequency: CONFIG.GAMMA_FREQUENCY,
                phi: CONFIG.PHI,
                version: '1.0.0',
            },
            merkle: {
                root: this.root,
                depth: this.tree.getDepth(),
                leaf_count: this.fighters.length,
            },
            statistics: {
                total_fighters: this.fighters.length,
                total_allocation: totalAllocation,
                allocation_by_tier: this.getAllocationByTier(),
            },
            fighters: this.fighters.map(f => ({
                ...f.toJSON(),
                proof: this.getProof(f.address).proof,
            })),
        };

        fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
        console.log(`\n⟨⦿⟩ Exported to ${outputPath}`);

        return data;
    }

    /**
     * @notice Get allocation breakdown by tier
     */
    getAllocationByTier() {
        const breakdown = {};
        for (const fighter of this.fighters) {
            if (!breakdown[fighter.tier]) {
                breakdown[fighter.tier] = { count: 0, total: 0 };
            }
            breakdown[fighter.tier].count += 1;
            breakdown[fighter.tier].total += fighter.allocation;
        }
        return breakdown;
    }

    /**
     * @notice Generate Solidity-compatible proof array
     */
    getSolidityProof(address) {
        const proofData = this.getProof(address);
        return proofData.proof.map(p => `bytes32(${p})`).join(',\n        ');
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
// GITHUB INTEGRATION (Mock for demonstration)
// ═══════════════════════════════════════════════════════════════════════════════

async function fetchGitHubStargazers(repo, token = null) {
    /**
     * In production, this would use the GitHub API:
     *
     * const response = await fetch(
     *     `https://api.github.com/repos/${repo}/stargazers`,
     *     { headers: token ? { Authorization: `token ${token}` } : {} }
     * );
     * return response.json();
     *
     * For now, return mock data.
     */
    console.log(`\n⟨⦿⟩ Fetching stargazers for ${repo}...`);

    // Mock stargazers (replace with real GitHub API call)
    return [
        { login: 'early_adopter_1', wallet: '0x1234567890123456789012345678901234567890' },
        { login: 'early_adopter_2', wallet: '0x2345678901234567890123456789012345678901' },
        { login: 'contributor_1', wallet: '0x3456789012345678901234567890123456789012' },
    ];
}

async function fetchGitHubContributors(repo, token = null) {
    console.log(`\n⟨⦿⟩ Fetching contributors for ${repo}...`);

    // Mock contributors (replace with real GitHub API call)
    return [
        { login: 'steffan', wallet: '0x0000000000000000000000000000000000000001', contributions: 500 },
        { login: 'dr_claude', wallet: '0x0000000000000000000000000000000000000002', contributions: 228 },
    ];
}

// ═══════════════════════════════════════════════════════════════════════════════
// MAIN EXECUTION
// ═══════════════════════════════════════════════════════════════════════════════

async function main() {
    console.log(`
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ⟨⦿⟩ QCI AIRDROP MERKLE GENERATOR ⟨⦿⟩                     ║
║                                                                              ║
║                  Identity: ${CONFIG.IDENTITY_HASH}                           ║
║                  Frequency: ${CONFIG.GAMMA_FREQUENCY}Hz                                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    `);

    const generator = new AirdropMerkleGenerator();

    // ═══════════════════════════════════════════════════════════════════════════
    // LOAD FROM INPUT FILE (The Book of Life)
    // ═══════════════════════════════════════════════════════════════════════════

    const inputFile = path.join(__dirname, 'merkle_input.json');
    if (fs.existsSync(inputFile)) {
        console.log(`\n⟨⦿⟩ Loading fighters from merkle_input.json (The Book of Life)...`);
        generator.loadFromFile(inputFile);
    } else {
        // Fallback to demo addresses if no input file
        console.log(`\n⟨⦿⟩ No input file found, using demo addresses...`);

        generator.addFighter(
            '0xSTEFFAN_WALLET_ADDRESS_HERE',
            'GENESIS_CONTRIBUTOR',
            CONFIG.MULTIPLIERS.EARLY_ADOPTER,
            { name: 'Steffan Douglas Haskins', role: 'Architect', github: 'steffan-haskins' }
        );

        const demoAddresses = [
            '0x1111111111111111111111111111111111111111',
            '0x2222222222222222222222222222222222222222',
            '0x3333333333333333333333333333333333333333',
            '0x4444444444444444444444444444444444444444',
            '0x5555555555555555555555555555555555555555',
        ];

        demoAddresses.forEach((addr, i) => {
            generator.addFighter(addr, 'FREEDOM_FIGHTER', 1.0, { demo: true, index: i });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // GENERATE TREE
    // ═══════════════════════════════════════════════════════════════════════════

    generator.generateTree();

    // ═══════════════════════════════════════════════════════════════════════════
    // EXPORT DATA
    // ═══════════════════════════════════════════════════════════════════════════

    const outputPath = path.join(__dirname, 'merkle_data.json');
    generator.exportToJSON(outputPath);

    // ═══════════════════════════════════════════════════════════════════════════
    // DEMONSTRATE PROOF GENERATION
    // ═══════════════════════════════════════════════════════════════════════════

    console.log('\n⟨⦿⟩ Example Proof Generation:');
    const firstFighter = generator.fighters[0];
    const exampleProof = generator.getProof(firstFighter.address);
    console.log(`   Address: ${exampleProof.address}`);
    console.log(`   Valid: ${exampleProof.isValid}`);
    console.log(`   Proof: ${JSON.stringify(exampleProof.proof, null, 2)}`);

    // ═══════════════════════════════════════════════════════════════════════════
    // SAVE MERKLE ROOT TO FILE
    // ═══════════════════════════════════════════════════════════════════════════

    const rootPath = path.join(__dirname, 'merkle_root.txt');
    fs.writeFileSync(rootPath, `MERKLE ROOT (THE BOOK OF LIFE)\n==============================\n\nRoot: ${generator.root}\nGenerated: ${new Date().toISOString()}\nFighters: ${generator.fighters.length}\n\nUse this root to deploy QCIPhoenixProtocol.\n\nThe city breathes at 40Hz.\nf(WHO) = WHO\n`);
    console.log(`\n⟨⦿⟩ Merkle root saved to merkle_root.txt`);

    // ═══════════════════════════════════════════════════════════════════════════
    // SOLIDITY DEPLOYMENT SNIPPET
    // ═══════════════════════════════════════════════════════════════════════════

    console.log(`
⟨⦿⟩ DEPLOYMENT SNIPPET:

// Deploy QCIPhoenixProtocol with this Merkle root:
bytes32 merkleRoot = ${generator.root};

QCIPhoenixProtocol protocol = new QCIPhoenixProtocol(merkleRoot);

// Example claim (from eligible address ${firstFighter.address}):
bytes32[] memory proof = new bytes32[](${generator.tree.getDepth()});
${generator.getSolidityProof(firstFighter.address)}
protocol.claimAirdrop(proof);
    `);

    console.log(`
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ⟨⦿⟩ ARMY ASSEMBLED ⟨⦿⟩                                   ║
║                                                                              ║
║   The city breathes at 40Hz.                                                 ║
║   f(WHO) = WHO                                                               ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    `);
}

// ═══════════════════════════════════════════════════════════════════════════════
// CLI INTERFACE
// ═══════════════════════════════════════════════════════════════════════════════

if (require.main === module) {
    main().catch(console.error);
}

module.exports = {
    AirdropMerkleGenerator,
    FreedomFighter,
    CONFIG,
};
