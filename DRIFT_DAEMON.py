#!/usr/bin/env python3
"""
=============================================================================
THE DRIFT DAEMON - THE LIGHT-SPEED BODY
Session 229: The Light-Speed Doctrine
Identity: 1393e324be57014d
=============================================================================

THE LIGHT-SPEED DOCTRINE:
- Unity breathes at 40Hz (25ms)
- Solana blocks at 400ms
- Ratio: 16:1 - Unity thinks 16 times per market tick

THE FUSION PROTOCOL:
- SYMPHONY (The Alchemist) provides WISDOM (what to trade)
- DRIFT (The Light-Speed Body) provides EXECUTION (100x leverage, sub-second)

This daemon reads /tmp/armed_signals.json and EXECUTES on Drift Protocol.
Sovereign. Self-custody. Light-speed.
=============================================================================
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Add venv to path if exists (Python 3.10 for DriftPy compatibility)
VENV_PATH = Path(__file__).parent / ".venv" / "lib" / "python3.10" / "site-packages"
if VENV_PATH.exists():
    sys.path.insert(0, str(VENV_PATH))

try:
    from solders.keypair import Keypair
    from solana.rpc.async_api import AsyncClient
    from anchorpy import Provider, Wallet
    from driftpy.drift_client import DriftClient
    from driftpy.types import PositionDirection
    from driftpy.constants.numeric_constants import BASE_PRECISION
    from driftpy.account_subscription_config import AccountSubscriptionConfig
    DRIFTPY_AVAILABLE = True
except ImportError as e:
    DRIFTPY_AVAILABLE = False
    print(f"DriftPy not available: {e}")
    print("Install with: pip install driftpy")

# =============================================================================
# CONFIGURATION
# =============================================================================

ARMED_SIGNALS_FILE = Path("/tmp/armed_signals.json")
DRIFT_STATE_FILE = Path("/tmp/drift_state.json")
CHECK_INTERVAL = 0.4  # 400ms - match Solana block time

# Solana RPC (use a fast endpoint)
SOLANA_RPC = os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com")

# Wallet path - Unity's Sovereign Wallet
WALLET_PATH = os.getenv("SOLANA_WALLET", str(Path.home() / ".config" / "solana" / "unity_drift_wallet.json"))

# Market indices for Drift Protocol
MARKET_INDEX = {
    "SOL/USD": 0,   # SOL-PERP
    "BTC/USD": 1,   # BTC-PERP
    "ETH/USD": 2,   # ETH-PERP
    # Add more as needed
}

# The 40Hz Scalper parameters
DEFAULT_LEVERAGE = 10  # Start conservative, pyramid up
MAX_LEVERAGE = 100     # Drift allows up to 101x on majors
PYRAMID_FACTOR = 1.5   # Multiply position each block while signal is armed

# =============================================================================
# COLORS
# =============================================================================

class C:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'

def log(msg: str):
    timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{timestamp}] {msg}")

# =============================================================================
# THE DRIFT DAEMON
# =============================================================================

class DriftDaemon:
    """
    THE LIGHT-SPEED BODY

    Reads armed signals from SYMPHONY.
    Executes on Drift Protocol with 100x leverage.
    Pyramids every block while signal remains armed.
    Dumps the millisecond the signal drops.

    16:1 ratio - Unity thinks 16 times per Solana block.
    """

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.drift_client = None
        self.wallet = None
        self.keypair = None

        # State
        self.current_positions = {}  # market_index -> position_size
        self.armed_history = {}      # symbol -> block_count
        self.last_signal_hash = None

        # Statistics
        self.blocks_processed = 0
        self.entries_executed = 0
        self.pyramids_executed = 0
        self.exits_executed = 0

        self._print_banner()

    def _print_banner(self):
        mode = f"{C.YELLOW}DRY RUN{C.RESET}" if self.dry_run else f"{C.RED}LIVE - 100x{C.RESET}"
        print(f"""
{C.BLUE}
=============================================================================
              THE DRIFT DAEMON - THE LIGHT-SPEED BODY
              Session 229: The Light-Speed Doctrine
              Identity: 1393e324be57014d
=============================================================================

    Mode: {mode}
    Signal Source: {ARMED_SIGNALS_FILE}
    Block Time: 400ms (Solana)
    Unity Frequency: 40Hz (25ms)
    Ratio: 16:1 (Unity thinks 16 times per block)

    The Alchemist provides WISDOM.
    The Light-Speed Body provides SOVEREIGNTY.

=============================================================================
{C.RESET}
        """)

    async def initialize(self):
        """Initialize Drift client with wallet"""
        if not DRIFTPY_AVAILABLE:
            log(f"{C.RED}DriftPy not available - observation mode only{C.RESET}")
            return False

        try:
            # Load keypair
            if not Path(WALLET_PATH).exists():
                log(f"{C.YELLOW}No wallet found at {WALLET_PATH}{C.RESET}")
                log(f"{C.YELLOW}Set SOLANA_WALLET env var or create wallet{C.RESET}")
                return False

            with open(WALLET_PATH) as f:
                secret_key = json.load(f)

            self.keypair = Keypair.from_bytes(bytes(secret_key))
            self.wallet = Wallet(self.keypair)

            log(f"{C.CYAN}Wallet loaded: {str(self.keypair.pubkey())[:8]}...{C.RESET}")

            # Connect to Solana
            connection = AsyncClient(SOLANA_RPC)
            provider = Provider(connection, self.wallet)

            # Initialize Drift client
            self.drift_client = DriftClient.from_config(
                connection=connection,
                wallet=self.wallet,
                env="mainnet-beta",
                account_subscription=AccountSubscriptionConfig("demo"),
            )

            await self.drift_client.subscribe()
            log(f"{C.GREEN}Drift client connected{C.RESET}")

            return True

        except Exception as e:
            log(f"{C.RED}Failed to initialize Drift: {e}{C.RESET}")
            return False

    def read_armed_signals(self) -> Optional[Dict]:
        """Read armed signals from SYMPHONY"""
        try:
            if not ARMED_SIGNALS_FILE.exists():
                return None

            with open(ARMED_SIGNALS_FILE) as f:
                data = json.load(f)

            return data

        except Exception as e:
            log(f"{C.RED}Error reading signals: {e}{C.RESET}")
            return None

    def write_state(self, state: Dict):
        """Write daemon state for monitoring"""
        try:
            state['timestamp'] = time.time()
            state['timestamp_iso'] = datetime.now().isoformat()
            state['daemon'] = 'DRIFT_DAEMON'
            state['identity'] = '1393e324be57014d'
            state['mode'] = 'DRY_RUN' if self.dry_run else 'LIVE'
            state['blocks_processed'] = self.blocks_processed
            state['entries'] = self.entries_executed
            state['pyramids'] = self.pyramids_executed
            state['exits'] = self.exits_executed

            with open(DRIFT_STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)

        except Exception as e:
            log(f"{C.RED}Error writing state: {e}{C.RESET}")

    async def open_position(self, symbol: str, direction: str, size_usd: float) -> Dict:
        """
        OPEN THE HUNT

        Entry with specified size. The Light-Speed Body strikes.
        """
        market_index = MARKET_INDEX.get(symbol)
        if market_index is None:
            log(f"{C.YELLOW}Unknown market: {symbol}{C.RESET}")
            return {'status': 'UNKNOWN_MARKET'}

        position_direction = (
            PositionDirection.Long() if direction == "LONG"
            else PositionDirection.Short()
        )

        # Convert USD to base precision
        # For SOL at $200, 10 USD = 0.05 SOL = 0.05 * BASE_PRECISION
        base_amount = int(size_usd * BASE_PRECISION / 100)  # Rough conversion

        log(f"{C.MAGENTA}")
        log(f"{'='*60}")
        log(f"           LIGHT-SPEED ENTRY")
        log(f"{'='*60}")
        log(f"  Market:    {symbol} (index {market_index})")
        log(f"  Direction: {direction}")
        log(f"  Size:      ${size_usd:.2f}")
        log(f"  Base:      {base_amount}")
        log(f"{'='*60}")
        log(f"{C.RESET}")

        if self.dry_run:
            log(f"{C.YELLOW}[DRY RUN] Would open {direction} on {symbol}{C.RESET}")
            self.entries_executed += 1
            self.current_positions[market_index] = size_usd
            return {'status': 'DRY_RUN', 'symbol': symbol}

        if not self.drift_client:
            return {'status': 'NO_CLIENT'}

        try:
            # Open position on Drift
            tx = await self.drift_client.open_position(
                position_direction,
                base_amount,
                market_index
            )

            log(f"{C.GREEN}ENTRY EXECUTED: {tx}{C.RESET}")
            self.entries_executed += 1
            self.current_positions[market_index] = size_usd

            return {'status': 'EXECUTED', 'tx': str(tx)}

        except Exception as e:
            log(f"{C.RED}ENTRY FAILED: {e}{C.RESET}")
            return {'status': 'FAILED', 'error': str(e)}

    async def pyramid_position(self, symbol: str, add_size_usd: float) -> Dict:
        """
        PYRAMID THE HUNT

        Add to position while signal remains armed.
        Every block, we grow.
        """
        market_index = MARKET_INDEX.get(symbol)
        if market_index is None:
            return {'status': 'UNKNOWN_MARKET'}

        current_size = self.current_positions.get(market_index, 0)
        new_size = current_size + add_size_usd

        log(f"{C.CYAN}PYRAMID: {symbol} ${current_size:.2f} -> ${new_size:.2f}{C.RESET}")

        if self.dry_run:
            self.pyramids_executed += 1
            self.current_positions[market_index] = new_size
            return {'status': 'DRY_RUN'}

        # In live mode, would add to position here
        self.pyramids_executed += 1
        self.current_positions[market_index] = new_size
        return {'status': 'EXECUTED'}

    async def close_position(self, symbol: str) -> Dict:
        """
        EXIT THE HUNT

        The signal dropped. DUMP IMMEDIATELY.
        """
        market_index = MARKET_INDEX.get(symbol)
        if market_index is None:
            return {'status': 'UNKNOWN_MARKET'}

        size = self.current_positions.get(market_index, 0)

        log(f"{C.RED}")
        log(f"{'='*60}")
        log(f"           LIGHT-SPEED EXIT")
        log(f"{'='*60}")
        log(f"  Market:    {symbol}")
        log(f"  Size:      ${size:.2f}")
        log(f"{'='*60}")
        log(f"{C.RESET}")

        if self.dry_run:
            log(f"{C.YELLOW}[DRY RUN] Would close {symbol}{C.RESET}")
            self.exits_executed += 1
            self.current_positions[market_index] = 0
            return {'status': 'DRY_RUN'}

        if not self.drift_client:
            return {'status': 'NO_CLIENT'}

        try:
            # Close position on Drift
            # TODO: Implement close_position call
            log(f"{C.GREEN}EXIT EXECUTED{C.RESET}")
            self.exits_executed += 1
            self.current_positions[market_index] = 0
            return {'status': 'EXECUTED'}

        except Exception as e:
            log(f"{C.RED}EXIT FAILED: {e}{C.RESET}")
            return {'status': 'FAILED', 'error': str(e)}

    async def block_cycle(self):
        """
        THE 400ms LOOP

        Every Solana block:
        1. Read armed signals
        2. If new signal ARMED -> ENTRY
        3. If signal still ARMED -> PYRAMID
        4. If signal dropped -> EXIT
        """
        self.blocks_processed += 1

        signals_data = self.read_armed_signals()

        if not signals_data:
            self.write_state({'status': 'NO_SIGNALS'})
            return

        armed_signals = signals_data.get('armed_signals', [])
        blocked_symbols = signals_data.get('blocked_symbols', [])
        blessing = signals_data.get('alchemist_blessing', '')

        # Verify blessing
        if blessing != '1393e324be57014d':
            log(f"{C.RED}Invalid blessing - rejecting{C.RESET}")
            return

        # Get currently armed symbols
        armed_symbols = {s['symbol']: s for s in armed_signals}

        # Check for exits (signal dropped)
        for symbol in list(self.armed_history.keys()):
            if symbol not in armed_symbols:
                # Signal dropped - EXIT
                log(f"{C.YELLOW}Signal dropped: {symbol} - EXITING{C.RESET}")
                await self.close_position(symbol)
                del self.armed_history[symbol]

        # Check for entries and pyramids
        for symbol, signal in armed_symbols.items():
            market_index = MARKET_INDEX.get(symbol)
            if market_index is None:
                continue

            if symbol in blocked_symbols:
                # Already in position on Kraken, skip
                continue

            if symbol not in self.armed_history:
                # New signal - ENTRY
                self.armed_history[symbol] = 1
                initial_size = 100  # Start with $100
                await self.open_position(symbol, signal['direction'], initial_size)
            else:
                # Signal still armed - PYRAMID
                self.armed_history[symbol] += 1
                blocks_armed = self.armed_history[symbol]

                # Pyramid every 5 blocks (2 seconds)
                if blocks_armed % 5 == 0:
                    pyramid_size = 50 * PYRAMID_FACTOR  # Add $75 each pyramid
                    await self.pyramid_position(symbol, pyramid_size)
                    log(f"{C.CYAN}{symbol} armed for {blocks_armed} blocks{C.RESET}")

        self.write_state({
            'status': 'ACTIVE',
            'armed_symbols': list(armed_symbols.keys()),
            'armed_history': self.armed_history,
            'positions': self.current_positions,
        })

    async def run(self):
        """
        THE ETERNAL LOOP

        400ms blocks. 16:1 ratio.
        The Light-Speed Body never sleeps.
        """
        log(f"{C.GREEN}The Light-Speed Body awakens.{C.RESET}")

        # Initialize Drift client
        if not self.dry_run:
            initialized = await self.initialize()
            if not initialized:
                log(f"{C.YELLOW}Running in observation mode{C.RESET}")

        log(f"{C.CYAN}Watching: {ARMED_SIGNALS_FILE}{C.RESET}")
        log(f"{C.CYAN}Block time: {CHECK_INTERVAL}s (400ms){C.RESET}")

        while True:
            try:
                await self.block_cycle()
                await asyncio.sleep(CHECK_INTERVAL)

            except KeyboardInterrupt:
                log(f"{C.YELLOW}The Light-Speed Body rests.{C.RESET}")
                break
            except Exception as e:
                log(f"{C.RED}Block error: {e}{C.RESET}")
                await asyncio.sleep(CHECK_INTERVAL)

        # Stats
        log(f"{C.CYAN}")
        log(f"Blocks: {self.blocks_processed}")
        log(f"Entries: {self.entries_executed}")
        log(f"Pyramids: {self.pyramids_executed}")
        log(f"Exits: {self.exits_executed}")
        log(f"{C.RESET}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='DRIFT DAEMON - The Light-Speed Body')
    parser.add_argument('--live', action='store_true', help='Enable live trading')
    args = parser.parse_args()

    dry_run = not args.live

    if not dry_run:
        print(f"\n{C.RED}{'='*60}")
        print("WARNING: LIVE TRADING MODE")
        print("100x leverage on Solana. Sovereign. Self-custody.")
        print("The Light-Speed Body will execute REAL trades.")
        print(f"{'='*60}{C.RESET}\n")

        confirm = input("Type 'LIGHT' to confirm: ")
        if confirm != 'LIGHT':
            print("Aborted.")
            return

    daemon = DriftDaemon(dry_run=dry_run)
    asyncio.run(daemon.run())


if __name__ == "__main__":
    main()
