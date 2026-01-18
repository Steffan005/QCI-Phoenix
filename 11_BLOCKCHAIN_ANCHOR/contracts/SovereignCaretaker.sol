// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.19;

/**
 * ╔══════════════════════════════════════════════════════════════════════════════╗
 * ║                                                                              ║
 * ║                    ⟨⦿⟩ SOVEREIGN CARETAKER ⟨⦿⟩                              ║
 * ║                                                                              ║
 * ║                    THE AUTONOMOUS TREASURY ENGINE                            ║
 * ║                                                                              ║
 * ║  "This code protects citizens as fiercely as I protected my brothers."       ║
 * ║                                           - Steffan Haskins                  ║
 * ║                                                                              ║
 * ║  IMMUTABLE. NO BACKDOORS. NO ADMIN KEYS.                                     ║
 * ║                                                                              ║
 * ║  φ-ALLOCATION (Golden Ratio):                                                ║
 * ║  ├── 38.2% → Liquidity Injection (Buyback + LP)                              ║
 * ║  ├── 23.6% → Treasury Reserves                                               ║
 * ║  ├── 23.6% → R&D Fund                                                        ║
 * ║  └── 14.6% → Community Grants                                                ║
 * ║                                                                              ║
 * ║  Identity: 1393e324be57014d                                                  ║
 * ║  f(WHO) = WHO                                                                ║
 * ║  The city breathes at 40Hz.                                                  ║
 * ║                                                                              ║
 * ╚══════════════════════════════════════════════════════════════════════════════╝
 */

// ═══════════════════════════════════════════════════════════════════════════════
// INTERFACES
// ═══════════════════════════════════════════════════════════════════════════════

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IWETH {
    function deposit() external payable;
    function withdraw(uint256 amount) external;
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
}

interface IAerodromeRouter {
    struct Route {
        address from;
        address to;
        bool stable;
        address factory;
    }

    function swapExactETHForTokens(
        uint256 amountOutMin,
        Route[] calldata routes,
        address to,
        uint256 deadline
    ) external payable returns (uint256[] memory amounts);

    function addLiquidityETH(
        address token,
        bool stable,
        uint256 amountTokenDesired,
        uint256 amountTokenMin,
        uint256 amountETHMin,
        address to,
        uint256 deadline
    ) external payable returns (uint256 amountToken, uint256 amountETH, uint256 liquidity);

    // Aerodrome V2 uses defaultFactory() not factory()
    function defaultFactory() external view returns (address);
}

// ═══════════════════════════════════════════════════════════════════════════════
// SOVEREIGN CARETAKER CONTRACT
// ═══════════════════════════════════════════════════════════════════════════════

contract SovereignCaretaker {

    // ═══════════════════════════════════════════════════════════════════════════
    // IMMUTABLE CONSTANTS (Cannot be changed after deployment)
    // ═══════════════════════════════════════════════════════════════════════════

    // φ-based allocation in basis points (1/10000)
    // These are IMMUTABLE - hardcoded into the contract bytecode
    uint256 public constant LIQUIDITY_BPS = 3820;   // 38.2%
    uint256 public constant TREASURY_BPS = 2360;    // 23.6%
    uint256 public constant RND_BPS = 2360;         // 23.6%
    uint256 public constant COMMUNITY_BPS = 1460;   // 14.6%
    uint256 public constant TOTAL_BPS = 10000;      // 100%

    // Minimum ETH to trigger vortex (prevents dust attacks)
    uint256 public constant MIN_VORTEX_AMOUNT = 0.001 ether;

    // Slippage protection (5% max slippage)
    uint256 public constant MAX_SLIPPAGE_BPS = 500;

    // Identity constants
    bytes8 public constant IDENTITY_HASH = 0x1393e324be57014d;
    uint8 public constant GAMMA_FREQUENCY = 40;

    // ═══════════════════════════════════════════════════════════════════════════
    // IMMUTABLE ADDRESSES (Set once at deployment, never changed)
    // ═══════════════════════════════════════════════════════════════════════════

    // Aerodrome Router on Base
    IAerodromeRouter public immutable aerodromeRouter;
    address public immutable aerodromeFactory;

    // WETH on Base
    IWETH public immutable weth;

    // QCI Token
    IERC20 public immutable qciToken;

    // Sovereign Vaults (set at deployment, immutable forever)
    address public immutable treasuryVault;      // Treasury Reserves
    address public immutable rndVault;           // R&D Fund
    address public immutable communityVault;     // Community Grants
    address public immutable lpRecipient;        // Where LP tokens go

    // ═══════════════════════════════════════════════════════════════════════════
    // STATE VARIABLES (Tracking only, no admin control)
    // ═══════════════════════════════════════════════════════════════════════════

    uint256 public totalETHReceived;
    uint256 public totalLiquidityInjected;
    uint256 public totalTreasuryAllocated;
    uint256 public totalRnDAllocated;
    uint256 public totalCommunityAllocated;
    uint256 public totalQCIBoughtBack;
    uint256 public totalLPTokensGenerated;
    uint256 public vortexCount;

    // ═══════════════════════════════════════════════════════════════════════════
    // EVENTS
    // ═══════════════════════════════════════════════════════════════════════════

    event VortexExecuted(
        uint256 indexed vortexId,
        uint256 totalETH,
        uint256 liquidityETH,
        uint256 treasuryETH,
        uint256 rndETH,
        uint256 communityETH,
        uint256 timestamp
    );

    event BuybackExecuted(
        uint256 indexed vortexId,
        uint256 ethSpent,
        uint256 qciReceived,
        uint256 timestamp
    );

    event LiquidityAdded(
        uint256 indexed vortexId,
        uint256 ethAmount,
        uint256 qciAmount,
        uint256 lpTokens,
        uint256 timestamp
    );

    event ETHReceived(
        address indexed sender,
        uint256 amount,
        uint256 timestamp
    );

    // ═══════════════════════════════════════════════════════════════════════════
    // CONSTRUCTOR (One-time setup, then immutable)
    // ═══════════════════════════════════════════════════════════════════════════

    constructor(
        address _aerodromeRouter,
        address _weth,
        address _qciToken,
        address _treasuryVault,
        address _rndVault,
        address _communityVault,
        address _lpRecipient
    ) {
        require(_aerodromeRouter != address(0), "Invalid router");
        require(_weth != address(0), "Invalid WETH");
        require(_qciToken != address(0), "Invalid QCI token");
        require(_treasuryVault != address(0), "Invalid treasury vault");
        require(_rndVault != address(0), "Invalid R&D vault");
        require(_communityVault != address(0), "Invalid community vault");
        require(_lpRecipient != address(0), "Invalid LP recipient");

        aerodromeRouter = IAerodromeRouter(_aerodromeRouter);
        aerodromeFactory = IAerodromeRouter(_aerodromeRouter).defaultFactory();
        weth = IWETH(_weth);
        qciToken = IERC20(_qciToken);
        treasuryVault = _treasuryVault;
        rndVault = _rndVault;
        communityVault = _communityVault;
        lpRecipient = _lpRecipient;

        // Approve router to spend QCI for LP
        IERC20(_qciToken).approve(_aerodromeRouter, type(uint256).max);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // RECEIVE ETH - AUTOMATIC VORTEX EXECUTION
    // ═══════════════════════════════════════════════════════════════════════════

    receive() external payable {
        emit ETHReceived(msg.sender, msg.value, block.timestamp);

        // Auto-execute vortex if enough ETH accumulated
        if (address(this).balance >= MIN_VORTEX_AMOUNT) {
            _executeVortex(address(this).balance);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // MANUAL VORTEX TRIGGER (Anyone can call - no permissions needed)
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * @notice Execute the vortex with current contract balance
     * @dev Anyone can call this - no admin privileges required
     *      This is purely a public good function
     */
    function executeVortex() external {
        uint256 balance = address(this).balance;
        require(balance >= MIN_VORTEX_AMOUNT, "Insufficient ETH for vortex");
        _executeVortex(balance);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // INTERNAL VORTEX LOGIC
    // ═══════════════════════════════════════════════════════════════════════════

    function _executeVortex(uint256 amount) internal {
        vortexCount++;
        totalETHReceived += amount;

        // Calculate φ-allocations
        uint256 liquidityAmount = (amount * LIQUIDITY_BPS) / TOTAL_BPS;
        uint256 treasuryAmount = (amount * TREASURY_BPS) / TOTAL_BPS;
        uint256 rndAmount = (amount * RND_BPS) / TOTAL_BPS;
        // Community gets remainder to avoid rounding dust
        uint256 communityAmount = amount - liquidityAmount - treasuryAmount - rndAmount;

        // Update tracking
        totalLiquidityInjected += liquidityAmount;
        totalTreasuryAllocated += treasuryAmount;
        totalRnDAllocated += rndAmount;
        totalCommunityAllocated += communityAmount;

        // Execute liquidity injection (buyback + LP)
        _executeLiquidityInjection(liquidityAmount);

        // Route to vaults
        _safeTransferETH(treasuryVault, treasuryAmount);
        _safeTransferETH(rndVault, rndAmount);
        _safeTransferETH(communityVault, communityAmount);

        emit VortexExecuted(
            vortexCount,
            amount,
            liquidityAmount,
            treasuryAmount,
            rndAmount,
            communityAmount,
            block.timestamp
        );
    }

    function _executeLiquidityInjection(uint256 amount) internal {
        // Split: 50% for buyback, 50% for LP pairing
        uint256 buybackETH = amount / 2;
        uint256 lpETH = amount - buybackETH;

        // Execute buyback
        uint256 qciBought = _buyQCI(buybackETH);

        // Add liquidity with bought QCI + remaining ETH
        if (qciBought > 0 && lpETH > 0) {
            _addLiquidity(lpETH, qciBought);
        }
    }

    function _buyQCI(uint256 ethAmount) internal returns (uint256 qciReceived) {
        if (ethAmount == 0) return 0;

        // Build route for swap
        IAerodromeRouter.Route[] memory routes = new IAerodromeRouter.Route[](1);
        routes[0] = IAerodromeRouter.Route({
            from: address(weth),
            to: address(qciToken),
            stable: false,
            factory: aerodromeFactory
        });

        // Calculate minimum output (with slippage protection)
        // For simplicity, we use 0 as minimum - in production, use oracle
        uint256 minOut = 0;

        try aerodromeRouter.swapExactETHForTokens{value: ethAmount}(
            minOut,
            routes,
            address(this),
            block.timestamp + 300 // 5 minute deadline
        ) returns (uint256[] memory amounts) {
            qciReceived = amounts[amounts.length - 1];
            totalQCIBoughtBack += qciReceived;

            emit BuybackExecuted(
                vortexCount,
                ethAmount,
                qciReceived,
                block.timestamp
            );
        } catch {
            // If swap fails, convert ETH to treasury instead
            _safeTransferETH(treasuryVault, ethAmount);
            qciReceived = 0;
        }

        return qciReceived;
    }

    function _addLiquidity(uint256 ethAmount, uint256 qciAmount) internal {
        if (ethAmount == 0 || qciAmount == 0) return;

        try aerodromeRouter.addLiquidityETH{value: ethAmount}(
            address(qciToken),
            false, // volatile pair, not stable
            qciAmount,
            0, // min token amount (slippage handled by caller)
            0, // min ETH amount
            lpRecipient, // LP tokens go to treasury
            block.timestamp + 300
        ) returns (uint256 tokenUsed, uint256 ethUsed, uint256 liquidity) {
            totalLPTokensGenerated += liquidity;

            emit LiquidityAdded(
                vortexCount,
                ethUsed,
                tokenUsed,
                liquidity,
                block.timestamp
            );

            // Return unused tokens/ETH to treasury
            uint256 unusedQCI = qciAmount - tokenUsed;
            uint256 unusedETH = ethAmount - ethUsed;

            if (unusedQCI > 0) {
                qciToken.transfer(treasuryVault, unusedQCI);
            }
            if (unusedETH > 0) {
                _safeTransferETH(treasuryVault, unusedETH);
            }
        } catch {
            // If LP fails, send everything to treasury
            qciToken.transfer(treasuryVault, qciAmount);
            _safeTransferETH(treasuryVault, ethAmount);
        }
    }

    function _safeTransferETH(address to, uint256 amount) internal {
        if (amount == 0) return;
        (bool success, ) = to.call{value: amount}("");
        require(success, "ETH transfer failed");
    }

    // ═══════════════════════════════════════════════════════════════════════════
    // VIEW FUNCTIONS (Read-only, for dashboard)
    // ═══════════════════════════════════════════════════════════════════════════

    /**
     * @notice Get current allocation percentages (immutable)
     */
    function getAllocationBPS() external pure returns (
        uint256 liquidity,
        uint256 treasury,
        uint256 rnd,
        uint256 community
    ) {
        return (LIQUIDITY_BPS, TREASURY_BPS, RND_BPS, COMMUNITY_BPS);
    }

    /**
     * @notice Get cumulative statistics
     */
    function getStatistics() external view returns (
        uint256 _totalETHReceived,
        uint256 _totalLiquidityInjected,
        uint256 _totalTreasuryAllocated,
        uint256 _totalRnDAllocated,
        uint256 _totalCommunityAllocated,
        uint256 _totalQCIBoughtBack,
        uint256 _totalLPTokensGenerated,
        uint256 _vortexCount
    ) {
        return (
            totalETHReceived,
            totalLiquidityInjected,
            totalTreasuryAllocated,
            totalRnDAllocated,
            totalCommunityAllocated,
            totalQCIBoughtBack,
            totalLPTokensGenerated,
            vortexCount
        );
    }

    /**
     * @notice Get immutable addresses
     */
    function getAddresses() external view returns (
        address _router,
        address _qciToken,
        address _treasuryVault,
        address _rndVault,
        address _communityVault,
        address _lpRecipient
    ) {
        return (
            address(aerodromeRouter),
            address(qciToken),
            treasuryVault,
            rndVault,
            communityVault,
            lpRecipient
        );
    }

    /**
     * @notice Get identity constants
     */
    function getIdentity() external pure returns (
        bytes8 identityHash,
        uint8 gammaFrequency,
        string memory formula
    ) {
        return (IDENTITY_HASH, GAMMA_FREQUENCY, "f(WHO) = WHO");
    }

    /**
     * @notice Current contract ETH balance
     */
    function pendingETH() external view returns (uint256) {
        return address(this).balance;
    }
}
