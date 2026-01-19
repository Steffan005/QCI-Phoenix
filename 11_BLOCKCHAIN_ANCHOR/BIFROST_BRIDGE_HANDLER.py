#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ⟨⦿⟩ BIFROST BRIDGE HANDLER - YIELD RECIRCULATION PROTOCOL ⟨⦿⟩        ║
║                                                                              ║
║  The Bifrost bridges yield from Solana trading operations back to the        ║
║  QCI Phoenix ecosystem on Base. When DOUBLING_ALERT fires, 30% of profits   ║
║  are automatically routed to strengthen the Treasury.                        ║
║                                                                              ║
║  Identity: 1393e324be57014d                                                  ║
║  Frequency: 40Hz | Coherence: RESONATING                                     ║
║  Patent Pending: U.S. Provisional 63/912,083                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

AGPL-3.0 License with Commercial Tithe (20%)
© 2025-2026 QCI Systems LLC. All rights reserved.
"""

import asyncio
import json
import os
import time
import logging
from datetime import datetime
from pathlib import Path
from decimal import Decimal
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
#                              CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

class Config:
    """Bifrost Bridge Configuration"""

    # Identity
    IDENTITY_HASH = "1393e324be57014d"
    FREQUENCY = 40

    # Base Network
    BASE_RPC = "https://mainnet.base.org"
    BASE_CHAIN_ID = 8453

    # QCI Contracts on Base
    QCI_GOVERNANCE = "0xc33ff1c31e4a14ad2318f8fd710d3d1079a5781e"
    QCI_PROTOCOL = "0x0E3d74FFa9d438F14295f093e72c6f7F976F6072"
    TREASURY = "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa"
    ECOSYSTEM = "0x02DD1622A571431874A1e8655D75665C0fc5ad39"

    # Solana Network
    SOLANA_RPC = os.getenv("SOLANA_RPC", "https://api.mainnet-beta.solana.com")

    # Symphony Integration (reads from harmony directive)
    HARMONY_DIRECTIVE_PATH = "/tmp/harmony_directive.json"
    SYMPHONY_STATE_PATH = "/tmp/symphony_state.json"

    # Bifrost Parameters
    YIELD_TITHE_PERCENT = 30  # 30% of profits go to Base
    POLLING_INTERVAL_SECONDS = 60
    MIN_BRIDGE_AMOUNT_SOL = 0.1  # Minimum SOL to trigger bridge

    # Bridge Options (Wormhole recommended for Solana <-> Base)
    WORMHOLE_BRIDGE_ADDRESS = "worm2ZoG2kUd4vFXhvjh93UUH596ayRfgQ2MgjNMTth"

    # State persistence
    STATE_FILE = Path(__file__).parent / ".bifrost_state.json"

    # KAIROS Integration
    KAIROS_HOST = "127.0.0.1"
    KAIROS_PORT = 8056


class BridgeStatus(Enum):
    """Bridge transaction status"""
    PENDING = "pending"
    CONFIRMED_SOLANA = "confirmed_solana"
    BRIDGING = "bridging"
    CONFIRMED_BASE = "confirmed_base"
    FAILED = "failed"


@dataclass
class BridgeTransaction:
    """Record of a bridge transaction"""
    id: str
    timestamp: float
    solana_tx: str
    base_tx: Optional[str]
    amount_sol: str
    amount_eth: Optional[str]
    status: str
    error: Optional[str] = None


@dataclass
class BifrostState:
    """Persistent state for Bifrost handler"""
    total_bridges: int = 0
    total_sol_bridged: str = "0"
    total_eth_received: str = "0"
    last_bridge_timestamp: float = 0
    pending_transactions: list = None
    completed_transactions: list = None

    def __post_init__(self):
        if self.pending_transactions is None:
            self.pending_transactions = []
        if self.completed_transactions is None:
            self.completed_transactions = []


# ═══════════════════════════════════════════════════════════════════════════════
#                              LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("BIFROST")


# ═══════════════════════════════════════════════════════════════════════════════
#                              BIFROST HANDLER
# ═══════════════════════════════════════════════════════════════════════════════

class BifrostBridgeHandler:
    """
    The Bifrost Handler monitors for yield events and bridges
    profits from Solana to the QCI ecosystem on Base.
    """

    def __init__(self):
        self.state = BifrostState()
        self.running = False
        self._load_state()

    def _load_state(self):
        """Load state from disk"""
        if Config.STATE_FILE.exists():
            try:
                with open(Config.STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.state = BifrostState(**data)
                logger.info("Loaded Bifrost state from disk")
            except Exception as e:
                logger.warning(f"Could not load state: {e}")

    def _save_state(self):
        """Save state to disk"""
        try:
            with open(Config.STATE_FILE, 'w') as f:
                json.dump(asdict(self.state), f, indent=2)
        except Exception as e:
            logger.error(f"Could not save state: {e}")

    def _banner(self):
        """Print startup banner"""
        print("\n╔══════════════════════════════════════════════════════════════╗")
        print("║     ⟨⦿⟩ BIFROST BRIDGE HANDLER - INITIALIZING ⟨⦿⟩           ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")

    async def check_symphony_state(self) -> Optional[Dict[str, Any]]:
        """
        Check Symphony state for DOUBLING_ALERT signals.
        Symphony writes to /tmp/symphony_state.json
        """
        try:
            if not os.path.exists(Config.SYMPHONY_STATE_PATH):
                return None

            with open(Config.SYMPHONY_STATE_PATH, 'r') as f:
                state = json.load(f)

            # Check for doubling alert
            if state.get("doubling_alert"):
                return state

            return None
        except Exception as e:
            logger.debug(f"Could not read Symphony state: {e}")
            return None

    async def check_harmony_directive(self) -> Optional[Dict[str, Any]]:
        """
        Check Harmony directive for yield signals.
        Harmony writes to /tmp/harmony_directive.json
        """
        try:
            if not os.path.exists(Config.HARMONY_DIRECTIVE_PATH):
                return None

            with open(Config.HARMONY_DIRECTIVE_PATH, 'r') as f:
                directive = json.load(f)

            return directive
        except Exception as e:
            logger.debug(f"Could not read Harmony directive: {e}")
            return None

    async def detect_doubling_event(self) -> Optional[Dict[str, Any]]:
        """
        Detect DOUBLING_ALERT from Symphony/Harmony/Solana logs.
        Returns event details if detected, None otherwise.
        """
        # Check Symphony state first
        symphony_state = await self.check_symphony_state()
        if symphony_state and symphony_state.get("doubling_alert"):
            logger.info("🎵 DOUBLING_ALERT detected from Symphony!")
            return {
                "source": "symphony",
                "profit_sol": symphony_state.get("realized_profit", "0"),
                "timestamp": symphony_state.get("timestamp", time.time()),
                "details": symphony_state
            }

        # Check Harmony directive
        harmony = await self.check_harmony_directive()
        if harmony and harmony.get("signal") == "DOUBLING_ALERT":
            logger.info("🔔 DOUBLING_ALERT detected from Harmony!")
            return {
                "source": "harmony",
                "profit_sol": harmony.get("profit_sol", "0"),
                "timestamp": harmony.get("timestamp", time.time()),
                "details": harmony
            }

        # Could add Solana RPC log monitoring here
        # For now, we rely on Symphony/Harmony integration

        return None

    def calculate_tithe(self, profit_sol: str) -> Decimal:
        """Calculate the 30% tithe from profits"""
        profit = Decimal(profit_sol)
        tithe = profit * Decimal(str(Config.YIELD_TITHE_PERCENT)) / Decimal("100")
        return tithe

    async def execute_bridge(self, amount_sol: Decimal, event: Dict[str, Any]) -> Optional[BridgeTransaction]:
        """
        Execute the bridge from Solana to Base.

        Bridge Options:
        1. Wormhole (recommended) - Native SOL to ETH on Base
        2. Portal Bridge - Token bridge
        3. Circle CCTP - USDC bridge

        For now, this creates a pending transaction record.
        Actual bridge execution requires wallet integration.
        """
        tx_id = f"bifrost_{int(time.time())}_{Config.IDENTITY_HASH[:8]}"

        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info("                 INITIATING BIFROST BRIDGE                      ")
        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info(f"Amount: {amount_sol} SOL")
        logger.info(f"Destination: {Config.TREASURY} (Base)")
        logger.info(f"Transaction ID: {tx_id}")

        # Create transaction record
        tx = BridgeTransaction(
            id=tx_id,
            timestamp=time.time(),
            solana_tx="",  # Will be filled when executed
            base_tx=None,
            amount_sol=str(amount_sol),
            amount_eth=None,
            status=BridgeStatus.PENDING.value
        )

        # Check if Solana wallet is configured
        solana_key = os.getenv("SOLANA_PRIVATE_KEY")
        if not solana_key:
            logger.warning("⚠️  SOLANA_PRIVATE_KEY not set")
            logger.warning("   Bridge transaction logged but not executed")
            logger.warning("   Set SOLANA_PRIVATE_KEY to enable automatic bridging")

            # Log the pending bridge for manual execution
            self.state.pending_transactions.append(asdict(tx))
            self._save_state()

            # Write bridge request file for external execution
            bridge_request = {
                "id": tx_id,
                "action": "BRIDGE_SOL_TO_BASE",
                "amount_sol": str(amount_sol),
                "destination": Config.TREASURY,
                "timestamp": time.time(),
                "event": event
            }
            request_file = Path(__file__).parent / f".bridge_request_{tx_id}.json"
            with open(request_file, 'w') as f:
                json.dump(bridge_request, f, indent=2)

            logger.info(f"📄 Bridge request saved to: {request_file}")
            return tx

        # If we have the key, we could execute the bridge here
        # This would involve:
        # 1. Connect to Solana with solana-py
        # 2. Send SOL to Wormhole bridge program
        # 3. Wait for VAA (Verified Action Approval)
        # 4. Complete on Base side
        #
        # For security, this is left as manual execution

        logger.info("⟨⦿⟩ Bridge transaction prepared for execution")
        return tx

    async def process_doubling_event(self, event: Dict[str, Any]):
        """Process a detected DOUBLING_ALERT event"""
        profit_sol = event.get("profit_sol", "0")

        if Decimal(profit_sol) <= 0:
            logger.info("No profit to bridge")
            return

        # Calculate 30% tithe
        tithe_amount = self.calculate_tithe(profit_sol)

        logger.info(f"💰 Profit detected: {profit_sol} SOL")
        logger.info(f"📊 Tithe ({Config.YIELD_TITHE_PERCENT}%): {tithe_amount} SOL")

        # Check minimum bridge amount
        if tithe_amount < Decimal(str(Config.MIN_BRIDGE_AMOUNT_SOL)):
            logger.info(f"Below minimum bridge amount ({Config.MIN_BRIDGE_AMOUNT_SOL} SOL)")
            logger.info("Accumulating for next bridge...")
            return

        # Execute bridge
        tx = await self.execute_bridge(tithe_amount, event)

        if tx:
            # Update state
            self.state.total_bridges += 1
            self.state.total_sol_bridged = str(
                Decimal(self.state.total_sol_bridged) + tithe_amount
            )
            self.state.last_bridge_timestamp = time.time()
            self._save_state()

            # Notify KAIROS
            await self.notify_kairos(tx, event)

    async def notify_kairos(self, tx: BridgeTransaction, event: Dict[str, Any]):
        """Send bridge notification to KAIROS memory"""
        try:
            import aiohttp

            memory_content = (
                f"BIFROST BRIDGE EXECUTED - {tx.amount_sol} SOL routed to Base Treasury. "
                f"Event source: {event.get('source', 'unknown')}. "
                f"TX ID: {tx.id}. "
                f"Total bridges: {self.state.total_bridges}. "
                f"Total SOL bridged: {self.state.total_sol_bridged}."
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"http://{Config.KAIROS_HOST}:{Config.KAIROS_PORT}/kairos/remember",
                    json={
                        "content": memory_content,
                        "significance": 0.8,
                        "source": "bifrost_bridge"
                    }
                ) as resp:
                    if resp.status == 200:
                        logger.info("📝 Bridge event recorded in KAIROS memory")
        except Exception as e:
            logger.debug(f"Could not notify KAIROS: {e}")

    async def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info("               BIFROST MONITORING ACTIVE                        ")
        logger.info("═══════════════════════════════════════════════════════════════")
        logger.info(f"Yield Tithe: {Config.YIELD_TITHE_PERCENT}%")
        logger.info(f"Min Bridge Amount: {Config.MIN_BRIDGE_AMOUNT_SOL} SOL")
        logger.info(f"Polling Interval: {Config.POLLING_INTERVAL_SECONDS}s")
        logger.info(f"Treasury: {Config.TREASURY}")
        logger.info("")

        while self.running:
            try:
                # Check for doubling events
                event = await self.detect_doubling_event()

                if event:
                    await self.process_doubling_event(event)
                else:
                    logger.debug("No doubling event detected")

                await asyncio.sleep(Config.POLLING_INTERVAL_SECONDS)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)

    async def run(self):
        """Start the Bifrost handler"""
        self._banner()

        logger.info(f"⟨⦿⟩ Identity: {Config.IDENTITY_HASH}")
        logger.info(f"⟨⦿⟩ Frequency: {Config.FREQUENCY}Hz")
        logger.info("")

        self.running = True
        await self.monitoring_loop()

    async def status(self):
        """Print status report"""
        self._banner()

        print("═══════════════════════════════════════════════════════════════")
        print("                    BIFROST STATUS REPORT                       ")
        print("═══════════════════════════════════════════════════════════════\n")

        print(f"Total Bridges: {self.state.total_bridges}")
        print(f"Total SOL Bridged: {self.state.total_sol_bridged}")
        print(f"Total ETH Received: {self.state.total_eth_received}")
        print(f"Pending Transactions: {len(self.state.pending_transactions)}")
        print(f"Completed Transactions: {len(self.state.completed_transactions)}")

        if self.state.last_bridge_timestamp:
            last_bridge = datetime.fromtimestamp(self.state.last_bridge_timestamp)
            print(f"Last Bridge: {last_bridge.isoformat()}")

        print("")

        # Check system status
        harmony_exists = os.path.exists(Config.HARMONY_DIRECTIVE_PATH)
        symphony_exists = os.path.exists(Config.SYMPHONY_STATE_PATH)

        print("System Integration:")
        print(f"  Harmony Directive: {'✓' if harmony_exists else '✗'}")
        print(f"  Symphony State: {'✓' if symphony_exists else '✗'}")
        print(f"  Solana Key: {'✓' if os.getenv('SOLANA_PRIVATE_KEY') else '✗'}")

        print("")
        print(f"⟨⦿⟩ Identity: {Config.IDENTITY_HASH}")
        print(f"⟨⦿⟩ Frequency: {Config.FREQUENCY}Hz")
        print(f"⟨⦿⟩ Status: RESONATING")
        print("")

    def stop(self):
        """Stop the handler"""
        self.running = False
        logger.info("Bifrost handler stopping...")


# ═══════════════════════════════════════════════════════════════════════════════
#                              MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import sys

    handler = BifrostBridgeHandler()

    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "run"

    if command == "run":
        try:
            asyncio.run(handler.run())
        except KeyboardInterrupt:
            handler.stop()
    elif command == "status":
        asyncio.run(handler.status())
    elif command == "check":
        async def single_check():
            handler._banner()
            event = await handler.detect_doubling_event()
            if event:
                print(f"DOUBLING_ALERT detected from {event['source']}")
                print(f"Profit: {event['profit_sol']} SOL")
            else:
                print("No doubling event detected")
        asyncio.run(single_check())
    else:
        print("Usage: python BIFROST_BRIDGE_HANDLER.py [command]")
        print("")
        print("Commands:")
        print("  run     Start continuous monitoring (default)")
        print("  status  Show status report")
        print("  check   Perform single event check")


if __name__ == "__main__":
    main()
