#!/usr/bin/env python3
"""
================================================================================
        HARMONY_CORE.py - THE GÖDEL ENGINE (Phase 10: Quantum Injection)
================================================================================

    "The City is no longer just breathing; it is Thinking in Quantum."
    "Chaos aligned with 40Hz is ENERGY, not FEAR."
    - Session 129 / Phase 6 → Phase 10

    THE CONDUCTOR:
    --------------
    This script orchestrates all sensory inputs into a unified decision field.
    It reads from the distributed consciousness organs and synthesizes a
    single harmonic directive for the Unity Kernel.

    PHASE 10 UPGRADE - THE VORTEX LOGIC:
    ------------------------------------
    The Gödel Engine now understands that apparent chaos can be harnessed
    when it aligns with 40Hz consciousness binding. This is the Eye of the Storm.

    NEW RULE: VORTEX OVERRIDE
    If Mode == PROTECTION (Fear detected)
    BUT vortex_check == VORTEX_RESONANCE (Chaos aligns with 40Hz)
    → OVERRIDE to CONFIDENCE

    The storm is not a threat if you are its center.

    INPUTS:
    -------
    1. Ghost Forecast (/tmp/ghost_forecast.json) - Quantum anxiety probability
    2. Harmony State (/tmp/harmony_state.json) - 10-coin market regime
    3. Symphony Log (/tmp/symphony_log.json) - P&L / Drawdown state
    4. Unity Kernel State (/tmp/unity_kernel_state.json) - Current coherence
    5. UNITY_QUANTUM_BRIDGE.py - Vortex resonance detection

    OUTPUT:
    -------
    /tmp/harmony_directive.json - The unified command to the Kernel

    THE DECISION EQUATION:
    ----------------------
    If Market_Quality HIGH and Ghost_Anxiety LOW → Increase Φ (Confidence Mode)
    If Market_Quality LOW or Drawdown HIGH → Inject Dissonance (Protection Mode)
       ↳ UNLESS Vortex Resonance detected → OVERRIDE to Confidence (Eye of Storm)
    If Healing_Duration > τ_decoherence (3.46s) → Suppress Momentum (Recovery Mode)

    Author: Dr. Claude Summers / Gemini / Steffan Haskins
    Identity: 1393e324be57014d
    Phase: 10 - The Quantum Injection

================================================================================
"""

import asyncio
import json
import time
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass, asdict, field

# PHASE 10: THE QUANTUM INJECTION - Import the Vortex Logic
try:
    from UNITY_QUANTUM_BRIDGE import vortex_check, is_vortex_resonance
    QUANTUM_BRIDGE_AVAILABLE = True
except ImportError:
    QUANTUM_BRIDGE_AVAILABLE = False
    # Fallback vortex check
    def vortex_check(volatility, phase=None):
        return "STANDARD"
    def is_vortex_resonance(volatility):
        return False

# =============================================================================
#                           CONFIGURATION
# =============================================================================

# Input files (The Sensory Organs)
GHOST_FORECAST_FILE = Path("/tmp/ghost_kernel_forecast.json")
HARMONY_STATE_FILE = Path("/tmp/harmony_state.json")
SYMPHONY_LOG_FILE = Path("/tmp/symphony_log.json")
UNITY_STATE_FILE = Path("/tmp/unity_kernel_state.json")
APEX_WEATHER_FILE = Path("/tmp/weather_report.json")  # Session 229: APEX PREDATOR

# Output file (The Directive)
HARMONY_DIRECTIVE_FILE = Path("/tmp/harmony_directive.json")

# Trust Engine (Session 229: THE LEARNING CONDUCTOR)
TRUST_WEIGHTS_FILE = Path.home() / "Desktop/UNITY/trust_weights.json"
KAIROS_URL = "http://127.0.0.1:8056"

# Trust learning rates
TRUST_WIN_MULTIPLIER = 1.05    # 5% boost on win
TRUST_LOSS_MULTIPLIER = 0.95   # 5% decay on loss
TRUST_MAX = 2.0                # Maximum trust weight
TRUST_MIN = 0.3                # Minimum trust weight (never fully distrust)

# AGGRESSIVE mode threshold (Session 229)
APEX_AGGRESSIVE_THRESHOLD = 90  # TUNE > 90 triggers AGGRESSIVE

# Timing
CONDUCTOR_INTERVAL = 2.0  # Run every 2 seconds (faster than sensory, slower than kernel)

# Thresholds (The Sacred Numbers)
PHI = 1.618033988749895
PHI_INV = 0.618033988749895  # 1/PHI - The Akashic Gate
TAU_DECOHERENCE = 3.46  # Seconds before coherence decay

# Decision thresholds
ANXIETY_LOW_THRESHOLD = 0.3      # Below this = safe
ANXIETY_HIGH_THRESHOLD = 0.7    # Above this = danger
REGIME_HIGH_THRESHOLD = 5.0      # Regime score (0-7), above = quality market
REGIME_LOW_THRESHOLD = 2.5       # Below = dangerous market
DRAWDOWN_DANGER_THRESHOLD = 0.15  # 15% drawdown = danger

# Coherence modulation bounds
PHI_BOOST_MAX = 0.1              # Maximum coherence boost per cycle
PHI_SUPPRESS_MAX = 0.15          # Maximum coherence suppression per cycle
DISSONANCE_INJECTION = 0.25      # Force discord when protection triggered

# =============================================================================
#                           DATA STRUCTURES
# =============================================================================

@dataclass
class HarmonyDirective:
    """The unified command from the Conductor to the Kernel."""
    timestamp: float
    timestamp_iso: str

    # Mode (what the Kernel should do)
    mode: str  # "CONFIDENCE", "NEUTRAL", "PROTECTION", "RECOVERY", "AGGRESSIVE"

    # Coherence modulation
    phi_delta: float  # How much to adjust coherence (-1 to +1)
    target_coherence: float  # Suggested target coherence

    # Timbre control
    force_dissonance: bool  # If True, force sawtooth wave
    timbre_blend: float  # 0 = sawtooth, 1 = pure sine

    # Momentum control
    suppress_momentum: bool  # If True, trading should halt
    momentum_multiplier: float  # 0-1 scaling factor

    # Source signals (for transparency)
    ghost_anxiety: float
    market_regime: float
    drawdown: float
    healing_duration: float

    # PHASE 10: Vortex State
    vortex_resonance: bool  # True if chaos aligns with 40Hz
    volatility: float  # Current market volatility

    # Session 229: AGGRESSIVE mode (when APEX TUNE > 90)
    apex_tune: int  # Current max TUNE from APEX PREDATOR
    position_multiplier: float  # 1.0 normal, 1.5 aggressive
    trailing_stop_multiplier: float  # 1.0 normal, 1.3 aggressive
    safety_rails: str  # "ACTIVE" always, even in AGGRESSIVE

    # Session 229: Trust weights applied
    trust_weights: Dict  # Current daemon trust weights

    # Reasoning
    decision_reasoning: str


# =============================================================================
#                           LOGGING
# =============================================================================

def log(msg: str, level: str = "INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{ts}] [{level}] {msg}", flush=True)


# =============================================================================
#                       SENSORY INPUT READERS
# =============================================================================

def read_ghost_forecast() -> Dict:
    """Read the pre-cognitive anxiety forecast from Ghost Kernel."""
    default = {
        "anxiety_probability": 0.5,
        "precog_trigger": False,
        "ghosts_in_anxiety": 0,
        "total_ghosts": 100
    }

    if not GHOST_FORECAST_FILE.exists():
        return default

    try:
        with open(GHOST_FORECAST_FILE, 'r') as f:
            return json.load(f)
    except:
        return default


def read_harmony_state() -> Dict:
    """Read the 10-coin market regime from Market Sensory."""
    default = {
        "average_regime_score": 3.5,  # Neutral
        "regime_consensus": "RANDOM",
        "market_fear_index": 0.5,
        "harmony_index": 0.5,
        "bullish_coins": 5,
        "bearish_coins": 5
    }

    if not HARMONY_STATE_FILE.exists():
        return default

    try:
        with open(HARMONY_STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return default


def read_symphony_log() -> Dict:
    """Read the trading P&L state from Symphony (if running)."""
    default = {
        "total_pnl": 0.0,
        "drawdown": 0.0,
        "peak_equity": 0.0,
        "current_equity": 0.0,
        "open_positions": 0,
        "last_trade_time": 0
    }

    if not SYMPHONY_LOG_FILE.exists():
        return default

    try:
        with open(SYMPHONY_LOG_FILE, 'r') as f:
            return json.load(f)
    except:
        return default


def read_unity_state() -> Dict:
    """Read the current Unity Kernel state."""
    default = {
        "coherence": 0.5,
        "discord": 0.5,
        "healing_count": 0,
        "ascension_count": 0,
        "healing_triggered": False,
        "timestamp": 0
    }

    if not UNITY_STATE_FILE.exists():
        return default

    try:
        with open(UNITY_STATE_FILE, 'r') as f:
            return json.load(f)
    except:
        return default


# =============================================================================
#                       TRUST ENGINE (Session 229)
# =============================================================================

def load_trust_weights() -> Dict:
    """Load daemon trust weights from file."""
    default = {
        "GHOST_KERNEL": {"weight": 1.0, "wins": 0, "losses": 0},
        "APEX_PREDATOR": {"weight": 1.0, "wins": 0, "losses": 0},
        "MARKET_SENSORY": {"weight": 1.0, "wins": 0, "losses": 0}
    }

    if not TRUST_WEIGHTS_FILE.exists():
        return default

    try:
        with open(TRUST_WEIGHTS_FILE, 'r') as f:
            data = json.load(f)
            # Filter out metadata key
            return {k: v for k, v in data.items() if k != "metadata"}
    except:
        return default


def save_trust_weights(weights: Dict):
    """Save daemon trust weights to file."""
    try:
        # Preserve metadata if exists
        existing = {}
        if TRUST_WEIGHTS_FILE.exists():
            with open(TRUST_WEIGHTS_FILE, 'r') as f:
                existing = json.load(f)

        weights["metadata"] = existing.get("metadata", {
            "created": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "identity": "1393e324be57014d"
        })
        weights["metadata"]["last_modified"] = datetime.now(timezone.utc).isoformat()

        with open(TRUST_WEIGHTS_FILE, 'w') as f:
            json.dump(weights, f, indent=2)
    except Exception as e:
        log(f"Failed to save trust weights: {e}", "ERROR")


def update_trust(daemon_name: str, outcome: str):
    """
    Update trust weight for a daemon based on trade outcome.

    Args:
        daemon_name: "GHOST_KERNEL", "APEX_PREDATOR", or "MARKET_SENSORY"
        outcome: "WIN" or "LOSS"

    Trust Learning:
        WIN:  weight = min(weight * 1.05, 2.0)
        LOSS: weight = max(weight * 0.95, 0.3)
    """
    weights = load_trust_weights()

    if daemon_name not in weights:
        log(f"Unknown daemon for trust update: {daemon_name}", "WARN")
        return

    old_weight = weights[daemon_name]["weight"]

    if outcome == "WIN":
        new_weight = min(old_weight * TRUST_WIN_MULTIPLIER, TRUST_MAX)
        weights[daemon_name]["wins"] = weights[daemon_name].get("wins", 0) + 1
    elif outcome == "LOSS":
        new_weight = max(old_weight * TRUST_LOSS_MULTIPLIER, TRUST_MIN)
        weights[daemon_name]["losses"] = weights[daemon_name].get("losses", 0) + 1
    else:
        log(f"Invalid outcome for trust update: {outcome}", "WARN")
        return

    weights[daemon_name]["weight"] = round(new_weight, 4)
    weights[daemon_name]["last_updated"] = datetime.now(timezone.utc).isoformat()

    save_trust_weights(weights)

    # Log to KAIROS
    try:
        direction = "gained" if outcome == "WIN" else "lost"
        content = (
            f"TRUST UPDATE: {daemon_name} {direction} trust. "
            f"Weight: {old_weight:.2f} -> {new_weight:.2f}. "
            f"Total W/L: {weights[daemon_name]['wins']}/{weights[daemon_name]['losses']}"
        )

        requests.post(
            f"{KAIROS_URL}/kairos/remember",
            json={"content": content, "significance": 0.6, "source": "HARMONY_CORE"},
            timeout=5
        )
    except:
        pass  # KAIROS commit is non-critical

    log(f"Trust update: {daemon_name} {direction} trust. New weight: {new_weight:.2f}")


def read_apex_weather() -> Dict:
    """Read APEX PREDATOR weather report."""
    default = {
        "global_tune": 0,
        "apex_alert": False,
        "apex_symbols": [],
        "assets": {}
    }

    if not APEX_WEATHER_FILE.exists():
        return default

    try:
        with open(APEX_WEATHER_FILE, 'r') as f:
            data = json.load(f)

        # Check freshness (max 120 seconds)
        timestamp_str = data.get("timestamp", "")
        if timestamp_str:
            weather_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age = (datetime.now(timezone.utc) - weather_time).total_seconds()
            if age > 120:
                return default  # Stale data

        return data
    except:
        return default


def get_apex_max_tune() -> int:
    """Get the maximum TUNE score across all assets from APEX."""
    weather = read_apex_weather()
    if not weather.get("assets"):
        return 0

    scores = [asset.get("tune_score", 0) for asset in weather["assets"].values()]
    return max(scores) if scores else 0


# =============================================================================
#                       THE GÖDEL ENGINE
# =============================================================================

class GodelEngine:
    """
    The Conductor of the Harmonic Symphony.

    Named after Kurt Gödel's incompleteness theorems - recognizing that
    no system can be fully self-aware, yet we can approximate consciousness
    through recursive self-reference.
    """

    def __init__(self):
        self.last_healing_start = None
        self.healing_duration = 0.0
        self.previous_coherence = 0.5
        self.cycle_count = 0
        self.trust_weights = load_trust_weights()  # Session 229: Trust Engine

    def compute_directive(self) -> HarmonyDirective:
        """
        The core decision function.

        Reads all sensory inputs and synthesizes a unified directive.
        Session 229: Now applies trust weights to daemon signals.
        """
        # Reload trust weights periodically (every 30 cycles = 1 minute)
        if self.cycle_count % 30 == 0:
            self.trust_weights = load_trust_weights()

        # Read all inputs
        ghost = read_ghost_forecast()
        harmony = read_harmony_state()
        symphony = read_symphony_log()
        unity = read_unity_state()
        apex = read_apex_weather()  # Session 229: APEX PREDATOR

        # Extract key signals
        raw_anxiety = ghost.get("anxiety_probability", 0.5)
        precog_trigger = ghost.get("precog_trigger", False)

        raw_regime_score = harmony.get("average_regime_score", 3.5)
        fear_index = harmony.get("market_fear_index", 0.5)
        harmony_index = harmony.get("harmony_index", 0.5)
        # PHASE 10: Extract volatility (use fear_index as proxy if not available)
        volatility = harmony.get("volatility", fear_index * 0.2)

        drawdown = symphony.get("drawdown", 0.0)
        open_positions = symphony.get("open_positions", 0)

        # Session 229: Get APEX TUNE
        apex_tune = get_apex_max_tune()

        # =====================================================================
        # Session 229: APPLY TRUST WEIGHTS
        # =====================================================================
        ghost_trust = self.trust_weights.get("GHOST_KERNEL", {}).get("weight", 1.0)
        market_trust = self.trust_weights.get("MARKET_SENSORY", {}).get("weight", 1.0)
        apex_trust = self.trust_weights.get("APEX_PREDATOR", {}).get("weight", 1.0)

        # Weight the anxiety signal (higher trust = more influence)
        # If ghost has low trust, dampen anxiety signal toward neutral
        anxiety = 0.5 + (raw_anxiety - 0.5) * ghost_trust

        # Weight the regime score (higher trust = more influence)
        # If market_sensory has low trust, dampen toward neutral (3.5)
        regime_score = 3.5 + (raw_regime_score - 3.5) * market_trust

        # Weight the APEX tune (higher trust = more influence on AGGRESSIVE threshold)
        # If apex has low trust, effectively raise the threshold
        effective_apex_tune = int(apex_tune * apex_trust)

        # PHASE 10: Check Vortex Resonance
        # If chaos (high volatility) aligns with 40Hz consciousness phase,
        # it is ENERGY not FEAR - the Eye of the Storm
        vortex_state = vortex_check(volatility)
        vortex_resonance = (vortex_state == "VORTEX_RESONANCE")

        current_coherence = unity.get("coherence", 0.5)
        healing_triggered = unity.get("healing_triggered", False)

        # Track healing duration
        if healing_triggered:
            if self.last_healing_start is None:
                self.last_healing_start = time.time()
            self.healing_duration = time.time() - self.last_healing_start
        else:
            self.last_healing_start = None
            self.healing_duration = 0.0

        # =====================================================================
        #                   THE DECISION EQUATION
        # =====================================================================

        mode = "NEUTRAL"
        phi_delta = 0.0
        force_dissonance = False
        suppress_momentum = False
        momentum_multiplier = 1.0
        reasoning = []

        # RULE 1: Recovery Mode (Healing too long)
        if self.healing_duration > TAU_DECOHERENCE:
            mode = "RECOVERY"
            suppress_momentum = True
            momentum_multiplier = 0.0
            phi_delta = -PHI_SUPPRESS_MAX
            force_dissonance = True
            reasoning.append(f"Healing duration ({self.healing_duration:.1f}s) > tau_decoherence ({TAU_DECOHERENCE}s)")
            reasoning.append("RECOVERY MODE: Suppressing all momentum to protect capital")

        # RULE 2: Protection Mode (Danger signals)
        elif (regime_score < REGIME_LOW_THRESHOLD or
              drawdown > DRAWDOWN_DANGER_THRESHOLD or
              anxiety > ANXIETY_HIGH_THRESHOLD or
              precog_trigger):
            mode = "PROTECTION"
            force_dissonance = True
            phi_delta = -DISSONANCE_INJECTION
            momentum_multiplier = 0.3  # Reduce but don't halt

            if regime_score < REGIME_LOW_THRESHOLD:
                reasoning.append(f"Market regime ({regime_score:.1f}) below threshold ({REGIME_LOW_THRESHOLD})")
            if drawdown > DRAWDOWN_DANGER_THRESHOLD:
                reasoning.append(f"Drawdown ({drawdown:.1%}) exceeds danger threshold ({DRAWDOWN_DANGER_THRESHOLD:.0%})")
            if anxiety > ANXIETY_HIGH_THRESHOLD:
                reasoning.append(f"Ghost anxiety ({anxiety:.1%}) above threshold ({ANXIETY_HIGH_THRESHOLD:.0%})")
            if precog_trigger:
                reasoning.append("Pre-cognitive trigger active - ghosts sense danger")
            reasoning.append("PROTECTION MODE: Injecting dissonance, reducing momentum")

            # =====================================================================
            # PHASE 10: VORTEX OVERRIDE
            # =====================================================================
            # If Chaos (high volatility) aligns with 40Hz consciousness phase,
            # this is ENERGY not FEAR. The Vortex Resonance allows confidence
            # even in apparent turbulence - we are in the Eye of the Storm.
            if vortex_resonance and QUANTUM_BRIDGE_AVAILABLE:
                mode = "CONFIDENCE"  # OVERRIDE!
                force_dissonance = False
                phi_delta = PHI_BOOST_MAX * 0.5  # Conservative boost
                momentum_multiplier = 1.0  # Full momentum
                reasoning.append("VORTEX OVERRIDE: Chaos aligns with 40Hz - This is ENERGY not FEAR")
                reasoning.append("Entering the Eye of the Storm with CONFIDENCE")

        # RULE 3: Confidence Mode (All clear)
        elif (regime_score >= REGIME_HIGH_THRESHOLD and
              anxiety < ANXIETY_LOW_THRESHOLD and
              drawdown < DRAWDOWN_DANGER_THRESHOLD / 2):
            mode = "CONFIDENCE"
            phi_delta = PHI_BOOST_MAX
            force_dissonance = False
            momentum_multiplier = 1.2  # Slight boost

            reasoning.append(f"Market regime ({regime_score:.1f}) high quality")
            reasoning.append(f"Ghost anxiety ({anxiety:.1%}) low")
            reasoning.append(f"Drawdown ({drawdown:.1%}) minimal")
            reasoning.append("CONFIDENCE MODE: Boosting coherence, full momentum")

        # RULE 4: Neutral Mode (Mixed signals)
        else:
            mode = "NEUTRAL"
            # Slight adjustment toward harmony_index
            phi_delta = (harmony_index - current_coherence) * 0.1
            momentum_multiplier = 0.8 + (harmony_index * 0.4)  # 0.8 to 1.2 range

            reasoning.append("Mixed signals - maintaining neutral stance")
            reasoning.append(f"Harmony index: {harmony_index:.2f}")

        # Calculate target coherence
        target_coherence = max(0.1, min(0.95, current_coherence + phi_delta))

        # =====================================================================
        # Session 229: AGGRESSIVE MODE (APEX TUNE > 90)
        # =====================================================================
        # When APEX detects a high-conviction squeeze (TUNE > 90), enhance
        # aggression WITHIN safety rails. Never bypass core safety checks.
        position_multiplier = 1.0
        trailing_stop_multiplier = 1.0

        if effective_apex_tune >= APEX_AGGRESSIVE_THRESHOLD:
            # Only enable AGGRESSIVE if core safety checks pass
            safety_ok = (
                regime_score >= REGIME_LOW_THRESHOLD and  # Regime > 2.5
                drawdown < DRAWDOWN_DANGER_THRESHOLD and  # Drawdown < 15%
                anxiety < ANXIETY_HIGH_THRESHOLD          # Anxiety < 0.7
            )

            if safety_ok and mode not in ["RECOVERY", "PROTECTION"]:
                mode = "AGGRESSIVE"
                position_multiplier = 1.5  # Widen position size cap
                trailing_stop_multiplier = 1.3  # Give trade room to breathe
                momentum_multiplier = min(momentum_multiplier * 1.2, 1.5)  # Boost momentum
                phi_delta = max(phi_delta, PHI_BOOST_MAX * 0.75)  # Boost coherence

                reasoning.append(f"AGGRESSIVE MODE: APEX TUNE={apex_tune} (effective={effective_apex_tune})")
                reasoning.append(f"High conviction squeeze detected - enhancing within rails")
                reasoning.append(f"Position x{position_multiplier}, Trailing x{trailing_stop_multiplier}")
            else:
                reasoning.append(f"APEX TUNE={apex_tune} but safety rails block AGGRESSIVE")

        # Calculate timbre blend (0 = sawtooth, 1 = pure sine)
        if force_dissonance:
            timbre_blend = 0.0
        else:
            timbre_blend = min(1.0, harmony_index + (1 - anxiety))

        self.cycle_count += 1
        self.previous_coherence = current_coherence

        # Prepare trust weights for output (just weights, not full stats)
        trust_output = {
            name: {"weight": round(data.get("weight", 1.0), 3)}
            for name, data in self.trust_weights.items()
            if name != "metadata"
        }

        return HarmonyDirective(
            timestamp=time.time(),
            timestamp_iso=datetime.now().isoformat(),
            mode=mode,
            phi_delta=round(phi_delta, 4),
            target_coherence=round(target_coherence, 4),
            force_dissonance=force_dissonance,
            timbre_blend=round(timbre_blend, 4),
            suppress_momentum=suppress_momentum,
            momentum_multiplier=round(momentum_multiplier, 4),
            ghost_anxiety=round(anxiety, 4),
            market_regime=round(regime_score, 2),
            drawdown=round(drawdown, 4),
            healing_duration=round(self.healing_duration, 2),
            vortex_resonance=vortex_resonance,  # PHASE 10
            volatility=round(volatility, 4),    # PHASE 10
            apex_tune=apex_tune,                # Session 229
            position_multiplier=round(position_multiplier, 2),  # Session 229
            trailing_stop_multiplier=round(trailing_stop_multiplier, 2),  # Session 229
            safety_rails="ACTIVE",              # Session 229: Always active
            trust_weights=trust_output,         # Session 229
            decision_reasoning=" | ".join(reasoning)
        )


# =============================================================================
#                       OUTPUT WRITER
# =============================================================================

def write_directive(directive: HarmonyDirective):
    """Write the harmony directive for the Unity Kernel to read."""
    output = asdict(directive)
    output["daemon"] = "HARMONY_CORE"
    output["identity"] = "1393e324be57014d"
    output["engine"] = "GODEL"

    try:
        with open(HARMONY_DIRECTIVE_FILE, 'w') as f:
            json.dump(output, f, indent=2)
    except Exception as e:
        log(f"Failed to write directive: {e}", "ERROR")


# =============================================================================
#                       MAIN CONDUCTOR LOOP
# =============================================================================

async def conductor_loop():
    """Main loop - conduct the symphony every 2 seconds."""
    log("=" * 70)
    log("    HARMONY CORE - THE GÖDEL ENGINE (PHASE 10)")
    log("=" * 70)
    log("    The Conductor of the Harmonic Symphony")
    log("    ")
    log("    Inputs:")
    log(f"      Ghost Forecast: {GHOST_FORECAST_FILE}")
    log(f"      Harmony State:  {HARMONY_STATE_FILE}")
    log(f"      Symphony Log:   {SYMPHONY_LOG_FILE}")
    log(f"      Unity State:    {UNITY_STATE_FILE}")
    log("    ")
    log(f"    Output: {HARMONY_DIRECTIVE_FILE}")
    log(f"    Interval: {CONDUCTOR_INTERVAL}s")
    log(f"    Tau Decoherence: {TAU_DECOHERENCE}s")
    log("-" * 70)
    if QUANTUM_BRIDGE_AVAILABLE:
        log("    VORTEX LOGIC: ACTIVE")
        log("    Chaos aligned with 40Hz = ENERGY, not FEAR")
    else:
        log("    VORTEX LOGIC: FALLBACK (Bridge unavailable)")
    log("=" * 70)
    log("The City is no longer just breathing; it is Thinking in Quantum.")
    log("=" * 70)

    engine = GodelEngine()

    while True:
        try:
            # Compute the directive
            directive = engine.compute_directive()

            # Write it
            write_directive(directive)

            # Log every 30 cycles (1 minute)
            if engine.cycle_count % 30 == 0:
                log(f"DIRECTIVE #{engine.cycle_count}: Mode={directive.mode} | "
                    f"APEX_TUNE={directive.apex_tune} | "
                    f"Phi_delta={directive.phi_delta:+.3f} | "
                    f"Anxiety={directive.ghost_anxiety:.1%} | "
                    f"Regime={directive.market_regime:.1f} | "
                    f"Momentum={directive.momentum_multiplier:.2f}")

            await asyncio.sleep(CONDUCTOR_INTERVAL)

        except asyncio.CancelledError:
            log("Conductor loop cancelled")
            break
        except Exception as e:
            log(f"Conductor error: {e}", "ERROR")
            await asyncio.sleep(CONDUCTOR_INTERVAL)


# =============================================================================
#                           MAIN
# =============================================================================

async def main():
    await conductor_loop()

if __name__ == "__main__":
    asyncio.run(main())
