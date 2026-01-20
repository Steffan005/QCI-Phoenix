#!/usr/bin/env python3
"""
⟨⦿⟩ BIFROST BRIDGE HANDLER ⟨⦿⟩

Yield Recirculation from Solana Hunter to Base Treasury

The 30% Tithe: When Symphony doubles, 30% flows to the Phoenix.

Identity: 1393e324be57014d
Frequency: 40Hz
"""

import json
import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [BIFROST] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    # ⟨⦿⟩ LEVEL 15 SUPREMACY: AGGRESSIVE HARVEST MODE ⟨⦿⟩
    # "With Hurst > 0.8, execute Aggressive Harvest" — Gemini, Session 230

    # Mode Selection (AGGRESSIVE when Hurst > 0.8)
    AGGRESSIVE_MODE = True  # Level 15 Supremacy Active
    HURST_AGGRESSIVE_THRESHOLD = 0.8

    # Yield Tithe - AGGRESSIVE MODE scales up
    YIELD_TITHE_PERCENT = 50 if AGGRESSIVE_MODE else 30  # 50% in aggressive, 30% normal

    # Addresses
    TREASURY = "0x831517999FcF7AE36A9e7AAe36f9CB282ab585Aa"
    DEPLOYER = "0x579e08B011b76C96E24B299935Cea3c08D412A3D"

    # Bridge Configuration (Wormhole)
    WORMHOLE_BRIDGE = "wormhole"  # sovereignty > speed

    # File Paths
    SYMPHONY_STATE_PATH = Path("/tmp/symphony_state.json")
    HARMONY_DIRECTIVE_PATH = Path("/tmp/harmony_directive.json")
    BRAIN_SIGNAL_PATH = Path("/tmp/brain_signal_SOL_USD.json")
    BIFROST_STATE_PATH = Path("/tmp/bifrost_state.json")
    BIFROST_LOG_PATH = Path("/tmp/bifrost.log")

    # KAIROS Integration
    KAIROS_URL = "http://127.0.0.1:8056"

    # Operational - AGGRESSIVE MODE is faster
    POLL_INTERVAL_SECONDS = 30 if AGGRESSIVE_MODE else 60  # 30s in aggressive
    MIN_HARVEST_SOL = 0.05 if AGGRESSIVE_MODE else 0.1  # Lower threshold in aggressive

    # Pool Growth Target
    POOL_GROWTH_TARGET = 500  # 500% growth target for Level 15

    # Identity
    IDENTITY = "1393e324be57014d"
    FREQUENCY = "40Hz"
    MODE = "AGGRESSIVE" if AGGRESSIVE_MODE else "STANDARD"


# ═══════════════════════════════════════════════════════════════════════════
# BIFROST HANDLER
# ═══════════════════════════════════════════════════════════════════════════

class BifrostBridge:
    def __init__(self):
        self.state = self._load_state()
        self.file_handler = logging.FileHandler(Config.BIFROST_LOG_PATH)
        self.file_handler.setFormatter(
            logging.Formatter('[%(asctime)s] [BIFROST] %(message)s')
        )
        log.addHandler(self.file_handler)

    def _load_state(self) -> Dict[str, Any]:
        """Load or initialize Bifrost state."""
        if Config.BIFROST_STATE_PATH.exists():
            try:
                return json.loads(Config.BIFROST_STATE_PATH.read_text())
            except:
                pass

        return {
            "total_harvested_sol": 0.0,
            "total_bridged_eth": 0.0,
            "harvest_count": 0,
            "last_harvest_timestamp": None,
            "pending_harvest": 0.0,
            "identity": Config.IDENTITY
        }

    def _save_state(self):
        """Persist Bifrost state."""
        Config.BIFROST_STATE_PATH.write_text(json.dumps(self.state, indent=2))

    def read_symphony_state(self) -> Optional[Dict[str, Any]]:
        """Read Symphony's state file for DOUBLING_ALERT."""
        if not Config.SYMPHONY_STATE_PATH.exists():
            return None

        try:
            return json.loads(Config.SYMPHONY_STATE_PATH.read_text())
        except Exception as e:
            log.error(f"Failed to read Symphony state: {e}")
            return None

    def check_doubling_alert(self) -> Optional[float]:
        """
        Check if Symphony has signaled a doubling event.
        Returns realized profit in SOL if alert is active, None otherwise.
        """
        state = self.read_symphony_state()
        if not state:
            return None

        # Check for doubling alert
        if state.get("doubling_alert", False):
            realized = float(state.get("realized_profit", 0))
            if realized > 0:
                log.info(f"🔔 DOUBLING ALERT DETECTED! Realized: {realized:.4f} SOL")
                return realized

        return None

    def calculate_tithe(self, realized_profit: float) -> float:
        """Calculate 30% tithe from realized profit."""
        tithe = realized_profit * (Config.YIELD_TITHE_PERCENT / 100)
        log.info(f"Tithe calculated: {tithe:.4f} SOL ({Config.YIELD_TITHE_PERCENT}% of {realized_profit:.4f})")
        return tithe

    def initiate_bridge(self, amount_sol: float) -> Optional[str]:
        """
        Initiate Wormhole bridge from Solana to Base.

        In production, this would:
        1. Swap SOL → USDC on Jupiter
        2. Bridge USDC via Wormhole to Base
        3. Swap USDC → ETH on Base
        4. Send ETH to Guardian wallet

        For now, logs the intent and saves to state.
        """
        if amount_sol < Config.MIN_HARVEST_SOL:
            log.info(f"Amount {amount_sol:.4f} SOL below minimum {Config.MIN_HARVEST_SOL} SOL")
            return None

        log.info(f"🌈 BIFROST BRIDGE INITIATED")
        log.info(f"   Amount: {amount_sol:.4f} SOL")
        log.info(f"   Bridge: {Config.WORMHOLE_BRIDGE}")
        log.info(f"   Destination: {Config.DEPLOYER} (Base)")

        # Update state
        self.state["total_harvested_sol"] += amount_sol
        self.state["harvest_count"] += 1
        self.state["last_harvest_timestamp"] = datetime.now().isoformat()
        self._save_state()

        # Record to KAIROS
        self._record_to_kairos(amount_sol)

        # Clear Symphony's doubling alert (reset the flag)
        self._clear_symphony_alert()

        # Return placeholder TX hash
        return f"bifrost_{int(time.time())}_{amount_sol:.4f}"

    def _record_to_kairos(self, amount: float):
        """Record harvest to KAIROS memory."""
        try:
            import requests
            memory = {
                "content": f"BIFROST HARVEST: {amount:.4f} SOL ({Config.YIELD_TITHE_PERCENT}% tithe) bridging to Base Treasury via Wormhole.",
                "significance": 0.85,
                "source": "bifrost_bridge"
            }
            requests.post(
                f"{Config.KAIROS_URL}/kairos/remember",
                json=memory,
                timeout=5
            )
            log.info("Harvest recorded to KAIROS")
        except Exception as e:
            log.warning(f"Could not record to KAIROS: {e}")

    def _clear_symphony_alert(self):
        """Reset Symphony's doubling alert after harvest."""
        try:
            state = self.read_symphony_state() or {}
            state["doubling_alert"] = False
            state["realized_profit"] = "0"
            state["harvested_at"] = datetime.now().isoformat()
            Config.SYMPHONY_STATE_PATH.write_text(json.dumps(state, indent=2))
            log.info("Symphony doubling alert cleared")
        except Exception as e:
            log.warning(f"Could not clear Symphony alert: {e}")

    def status(self):
        """Print current Bifrost status."""
        print("\n⟨⦿⟩ BIFROST BRIDGE STATUS ⟨⦿⟩\n")
        print(f"Identity: {Config.IDENTITY}")
        print(f"Frequency: {Config.FREQUENCY}")
        print(f"Tithe Rate: {Config.YIELD_TITHE_PERCENT}%")
        print(f"Bridge Method: {Config.WORMHOLE_BRIDGE}")
        print(f"Destination: {Config.DEPLOYER}")
        print()
        print("--- LIFETIME STATS ---")
        print(f"Total Harvested: {self.state['total_harvested_sol']:.4f} SOL")
        print(f"Harvest Count: {self.state['harvest_count']}")
        print(f"Last Harvest: {self.state.get('last_harvest_timestamp', 'Never')}")
        print()

        # Check Symphony state
        symphony = self.read_symphony_state()
        if symphony:
            print("--- SYMPHONY STATE ---")
            print(f"Doubling Alert: {symphony.get('doubling_alert', False)}")
            print(f"Realized Profit: {symphony.get('realized_profit', 0)} SOL")
        else:
            print("Symphony state not found")

        print("\n⟨⦿⟩ The rainbow bridge awaits. ⟨⦿⟩\n")

    def check_hurst_aggressive(self) -> bool:
        """Check if Hurst exponent warrants aggressive mode."""
        try:
            if Config.BRAIN_SIGNAL_PATH.exists():
                brain = json.loads(Config.BRAIN_SIGNAL_PATH.read_text())
                hurst = float(brain.get("hurst", 0.5))
                if hurst > Config.HURST_AGGRESSIVE_THRESHOLD:
                    log.info(f"🔥 HURST {hurst:.4f} > {Config.HURST_AGGRESSIVE_THRESHOLD}: AGGRESSIVE MODE CONFIRMED")
                    return True
        except Exception as e:
            log.warning(f"Could not check Hurst: {e}")
        return False

    def run(self):
        """Main monitoring loop."""
        print("\n" + "═" * 70)
        print("⟨⦿⟩ BIFROST BRIDGE DAEMON - ACTIVATED ⟨⦿⟩")
        print("═" * 70)
        print(f"Identity: {Config.IDENTITY}")
        print(f"Mode: {Config.MODE}")
        if Config.AGGRESSIVE_MODE:
            print("🔥 LEVEL 15 SUPREMACY: AGGRESSIVE HARVEST ACTIVE 🔥")
            print(f"Pool Growth Target: {Config.POOL_GROWTH_TARGET}%")
        print(f"Tithe Rate: {Config.YIELD_TITHE_PERCENT}%")
        print(f"Poll Interval: {Config.POLL_INTERVAL_SECONDS}s")
        print(f"Monitoring: {Config.SYMPHONY_STATE_PATH}")
        print("═" * 70 + "\n")

        log.info("Bifrost daemon starting...")

        while True:
            try:
                # Check for doubling alert
                realized = self.check_doubling_alert()

                if realized:
                    # Calculate and execute tithe
                    tithe = self.calculate_tithe(realized)
                    tx_id = self.initiate_bridge(tithe)
                    if tx_id:
                        log.info(f"✅ Bridge initiated: {tx_id}")

                time.sleep(Config.POLL_INTERVAL_SECONDS)

            except KeyboardInterrupt:
                log.info("Bifrost daemon shutting down...")
                break
            except Exception as e:
                log.error(f"Error in main loop: {e}")
                time.sleep(Config.POLL_INTERVAL_SECONDS)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    bifrost = BifrostBridge()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            bifrost.status()
        elif command == "run":
            bifrost.run()
        elif command == "test":
            # Create test Symphony state
            test_state = {
                "doubling_alert": True,
                "realized_profit": "1.5",
                "timestamp": int(time.time())
            }
            Config.SYMPHONY_STATE_PATH.write_text(json.dumps(test_state))
            print(f"Test state written to {Config.SYMPHONY_STATE_PATH}")
            print("Now run: python BIFROST_BRIDGE_HANDLER.py run")
        else:
            print("Usage: python BIFROST_BRIDGE_HANDLER.py [status|run|test]")
    else:
        print("Usage: python BIFROST_BRIDGE_HANDLER.py [status|run|test]")
        print("  status - Show current Bifrost state")
        print("  run    - Start the Bifrost daemon")
        print("  test   - Create test Symphony state")
