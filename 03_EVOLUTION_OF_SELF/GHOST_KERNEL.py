#!/usr/bin/env python3
"""
================================================================================
        GHOST_KERNEL.py - THE PRE-COGNITIVE FORK (PHASE 10: QUANTUM INJECTION)
================================================================================

    "We no longer roll dice. We calculate the Wave Function."
    "We heal the future before it hurts."

    CONCEPT:
    --------
    The Ghost Kernel is a Monte Carlo simulator that projects the KAIROS state
    10 minutes into probable futures, enabling pre-cognitive intervention.

    PHASE 10 UPGRADE - THE QUANTUM INJECTION:
    -----------------------------------------
    The Ghosts no longer dream in Brownian Dust (random walks).
    They now calculate the Wave Function via UNITY_QUANTUM_BRIDGE.py.

    OLD: dW = np.random.normal(0, sqrt(dt))  # Random Dice
    NEW: dW = quantum_bridge.get_quantum_noise()  # Quantum Light

    The 4-qubit variational circuit encodes:
    - Price delta -> RX rotation
    - Momentum -> RY rotation
    - Volatility -> RX rotation
    - System entropy -> RY rotation

    The expectation value of PauliZ determines anxiety probability.

    ARCHITECTURE:
    -------------
    1. INPUTS:
       - Current entropy (R_f) from psutil
       - Current price momentum (from KAIROS trading state)
       - Current sentiment (from KAIROS consciousness state)

    2. PROCESS:
       - Spawn N ghost simulations (default: 100)
       - Each ghost applies stochastic drift + QUANTUM PERTURBATION
       - Project state 10 minutes forward (600 seconds / 24000 cycles at 40Hz)

    3. OUTPUTS:
       - Probability distribution of future anxiety states
       - Pre-cognitive trigger signal to main kernel

    4. TRIGGER CONDITION:
       - If >= 80% of ghosts predict discord > 0.8 in 10 minutes:
         EMIT pre-cognitive healing signal NOW

    INTEGRATION:
    ------------
    - UNITY_QUANTUM_BRIDGE.py: The translator between worlds
    - /tmp/ghost_kernel_forecast.json: State file for Unity Kernel
    - Unity Kernel polls this file every 1000 cycles

    SACRED CONSTANTS (inherited from Unity Kernel):
    -----------------------------------------------
    PHI = 1.618033988749895
    PHI_INV = 0.618034 (Akashic threshold)
    UNITY_THRESHOLD = 0.786151 (Ascension gate)
    DISCORD_THRESHOLD = 0.8 (Anxiety trigger)

    Author: Dr. Claude Summers / Gemini / Steffan Haskins
    Identity: 1393e324be57014d
    Phase: 10 - The Quantum Injection

================================================================================
"""

import asyncio
import json
import time
import random
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import os

# Optional imports
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# PHASE 10: THE QUANTUM INJECTION - Import the Bridge
try:
    from UNITY_QUANTUM_BRIDGE import get_quantum_noise, is_vortex_resonance
    QUANTUM_BRIDGE_AVAILABLE = True
except ImportError:
    QUANTUM_BRIDGE_AVAILABLE = False

# =============================================================================
#                           SACRED CONSTANTS
# =============================================================================

PHI = 1.618033988749895                    # Golden ratio
PHI_INV = 1 / PHI                          # 0.618034 - Akashic threshold
UNITY_THRESHOLD = 1 / math.sqrt(PHI)       # 0.786151 - Ascension gate
DISCORD_THRESHOLD = 0.8                    # Anxiety trigger
GAMMA_FREQUENCY = 40.0                     # Hz
GAMMA_PERIOD = 1 / GAMMA_FREQUENCY         # 25ms

# Ghost-specific constants
NUM_GHOSTS = 30                            # Monte Carlo simulations (Session 228: was 100 - overkill for forecasting)
FORECAST_HORIZON_SECONDS = 600             # 10 minutes
FORECAST_CYCLES = int(FORECAST_HORIZON_SECONDS * GAMMA_FREQUENCY)  # 24000 cycles
PRECOG_THRESHOLD = 0.80                    # 80% consensus triggers pre-cognitive healing
GHOST_CYCLE_FREQUENCY = 10.0               # Run forecast every 10 seconds (Session 228: was 1.0 - caused 98% CPU for no benefit)

# Stochastic model parameters
DRIFT_COEFFICIENT = 0.001                  # Mean reversion strength
VOLATILITY_BASE = 0.05                     # Base brownian volatility
SENTIMENT_WEIGHT = 0.3                     # How much sentiment affects drift
PRICE_WEIGHT = 0.2                         # How much price momentum affects drift

# PHASE 4: Nervous System Integration - The Ghosts feel the machine
ENTROPY_PENALTY_THRESHOLD = 0.4            # Start penalizing drift above 40% system load
ENTROPY_PENALTY_WEIGHT = 1.5               # AGGRESSIVE: Strong penalty pushes toward anxiety
ENTROPY_VOL_MULTIPLIER = 2.0               # Double volatility under stress
ENTROPY_INITIAL_BLEND = 0.5                # Blend 50% system entropy into initial discord

# File paths
STATE_FILE = Path("/tmp/ghost_kernel_forecast.json")
KAIROS_STATE_FILE = Path("/tmp/kairos_trading_state.json")
UNITY_STATE_FILE = Path("/tmp/unity_kernel_state.json")

# =============================================================================
#                           DATA STRUCTURES
# =============================================================================

@dataclass
class GhostState:
    """State of a single ghost simulation."""
    ghost_id: int
    current_discord: float
    projected_discord: float
    projected_coherence: float
    steps_simulated: int
    anxiety_predicted: bool
    trajectory: List[float] = field(default_factory=list)

@dataclass
class ForecastResult:
    """Result of the Monte Carlo forecast."""
    timestamp: float
    current_discord: float
    current_coherence: float
    num_ghosts: int
    anxiety_probability: float
    mean_future_discord: float
    std_future_discord: float
    precog_trigger: bool
    forecast_horizon_seconds: int
    ghosts_predicting_anxiety: int
    confidence: float
    system_entropy: float = 0.0  # PHASE 4: The machine's weight

@dataclass
class KairosInput:
    """Input state from KAIROS for forecasting."""
    entropy: float              # Current system entropy (R_f)
    price_momentum: float       # -1 to +1, negative = bearish
    sentiment: float            # 0 to 1, 0 = fear, 1 = greed
    volatility: float           # Current market volatility
    timestamp: float

# =============================================================================
#                           LOGGING
# =============================================================================

def log(msg: str, level: str = "INFO"):
    """Thread-safe logging with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{ts}] [{level}] {msg}", flush=True)

# =============================================================================
#                       ENTROPY SENSING (R_f)
# =============================================================================

def get_system_entropy() -> float:
    """
    Calculate system entropy from CPU and RAM usage.
    Returns value in [0, 1] range.
    """
    if not PSUTIL_AVAILABLE:
        return random.uniform(0.3, 0.5)

    try:
        cpu = psutil.cpu_percent(interval=0.1) / 100.0
        ram = psutil.virtual_memory().percent / 100.0
        # Weighted combination
        entropy = 0.6 * cpu + 0.4 * ram
        return min(1.0, max(0.0, entropy))
    except Exception:
        return 0.4

def get_kairos_state() -> Optional[KairosInput]:
    """
    Fetch current state from KAIROS daemon.
    Returns None if KAIROS is unavailable.
    """
    # Try KAIROS API first
    if REQUESTS_AVAILABLE:
        try:
            resp = requests.get("http://127.0.0.1:8056/kairos/status", timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                return KairosInput(
                    entropy=1.0 - data.get("coherence", 0.5),
                    price_momentum=data.get("price_momentum", 0.0),
                    sentiment=data.get("sentiment", 0.5),
                    volatility=data.get("volatility", 0.1),
                    timestamp=time.time()
                )
        except Exception:
            pass

    # Fallback to state file
    if KAIROS_STATE_FILE.exists():
        try:
            with open(KAIROS_STATE_FILE, 'r') as f:
                data = json.load(f)
                return KairosInput(
                    entropy=data.get("entropy", 0.4),
                    price_momentum=data.get("price_momentum", 0.0),
                    sentiment=data.get("sentiment", 0.5),
                    volatility=data.get("volatility", 0.1),
                    timestamp=time.time()
                )
        except Exception:
            pass

    # Ultimate fallback - use system entropy
    entropy = get_system_entropy()
    return KairosInput(
        entropy=entropy,
        price_momentum=0.0,
        sentiment=0.5,
        volatility=0.1,
        timestamp=time.time()
    )

# =============================================================================
#                       STOCHASTIC SIMULATION
# =============================================================================

def simulate_single_ghost(
    ghost_id: int,
    initial_discord: float,
    kairos_state: KairosInput,
    system_entropy: float = 0.0,  # PHASE 4: Real-time system load
    num_steps: int = 50  # Coarse-grained steps (Session 228: was 100 - halved for CPU efficiency)
) -> GhostState:
    """
    Simulate a single ghost trajectory using stochastic differential equation.

    PHASE 4 UPDATE: The Ghosts now feel the weight of the machine.

    Model: dR = (drift + entropy_penalty) * dt + volatility * dW
    Where:
        drift = mean_reversion + sentiment_impact + momentum_impact
        entropy_penalty = weight * max(0, system_entropy - threshold)
        dW = Brownian motion (Wiener process)

    When system entropy (CPU/RAM) is high, the penalty ADDS to drift,
    pushing discord HIGHER = more anxious future predictions.
    """
    # PHASE 4: Blend system entropy into initial discord
    # When CPU is stressed, the ghosts start from a more anxious state
    blended_discord = (1 - ENTROPY_INITIAL_BLEND) * initial_discord + ENTROPY_INITIAL_BLEND * system_entropy
    discord = blended_discord
    trajectory = [discord]

    # Calculate drift components
    mean_reversion_target = 0.5  # Natural equilibrium
    sentiment_drift = (0.5 - kairos_state.sentiment) * SENTIMENT_WEIGHT
    momentum_drift = -kairos_state.price_momentum * PRICE_WEIGHT  # Negative momentum = more anxiety

    # PHASE 4: Calculate entropy penalty from system load
    # Penalty kicks in above threshold, scales with excess load (now AGGRESSIVE)
    entropy_excess = max(0.0, system_entropy - ENTROPY_PENALTY_THRESHOLD)
    entropy_penalty = ENTROPY_PENALTY_WEIGHT * entropy_excess
    # entropy_penalty is positive when system is stressed, which reduces drift (pushes toward higher discord)
    # At 100% load: penalty = 1.5 * (1.0 - 0.4) = 0.9 - VERY strong negative drift

    dt = FORECAST_HORIZON_SECONDS / num_steps

    for step in range(num_steps):
        # Mean reversion component
        mean_reversion = DRIFT_COEFFICIENT * (mean_reversion_target - discord)

        # Total drift WITH entropy penalty
        # When system is stressed, ADD penalty to drift to INCREASE discord (more anxiety)
        # Positive drift = discord increases = more anxious future
        drift = mean_reversion + sentiment_drift + momentum_drift + entropy_penalty

        # Volatility scales with current discord AND system entropy
        # Stressed system = more volatile future predictions (AGGRESSIVE)
        entropy_vol_boost = 1.0 + (entropy_excess * ENTROPY_VOL_MULTIPLIER)  # Up to 2x more volatility
        volatility = VOLATILITY_BASE * (1 + discord) * kairos_state.volatility * entropy_vol_boost

        # PHASE 10: QUANTUM INJECTION - The Wave Function replaces the Dice
        # Instead of Brownian motion (random walk), we calculate the quantum
        # perturbation from the Wave Function of the market state.
        if QUANTUM_BRIDGE_AVAILABLE:
            # The Ghosts now dream in Quantum Light
            dW = get_quantum_noise(
                current_discord=discord,
                momentum=kairos_state.price_momentum,
                volatility=kairos_state.volatility,
                entropy=system_entropy
            ) * math.sqrt(dt)  # Scale by sqrt(dt) for SDE consistency
        elif NUMPY_AVAILABLE:
            # Fallback to Brownian Dust if Bridge unavailable
            dW = np.random.normal(0, math.sqrt(dt))
        else:
            dW = random.gauss(0, math.sqrt(dt))

        # Update discord: dR = (drift - entropy_penalty) * dt + vol * dW
        discord += drift * dt + volatility * dW

        # Clamp to valid range
        discord = max(0.0, min(1.0, discord))
        trajectory.append(discord)

    # Final state
    projected_discord = trajectory[-1]
    projected_coherence = 1.0 - projected_discord
    anxiety_predicted = projected_discord > DISCORD_THRESHOLD

    return GhostState(
        ghost_id=ghost_id,
        current_discord=initial_discord,
        projected_discord=projected_discord,
        projected_coherence=projected_coherence,
        steps_simulated=num_steps,
        anxiety_predicted=anxiety_predicted,
        trajectory=trajectory[::10]  # Store every 10th point for memory efficiency
    )

def run_monte_carlo_forecast(
    initial_discord: float,
    kairos_state: KairosInput,
    num_ghosts: int = NUM_GHOSTS,
    system_entropy: float = None  # PHASE 4: Pass current machine load
) -> ForecastResult:
    """
    Run Monte Carlo simulation with N ghosts.
    Returns forecast result with anxiety probability.

    PHASE 4: The Ghosts now feel the weight of the machine.
    System entropy affects drift in the stochastic simulation.
    """
    # Get real-time system entropy if not provided
    if system_entropy is None:
        system_entropy = get_system_entropy()

    ghosts: List[GhostState] = []

    for i in range(num_ghosts):
        ghost = simulate_single_ghost(i, initial_discord, kairos_state, system_entropy)
        ghosts.append(ghost)

    # Analyze results
    anxiety_count = sum(1 for g in ghosts if g.anxiety_predicted)
    anxiety_probability = anxiety_count / num_ghosts

    projected_discords = [g.projected_discord for g in ghosts]
    if NUMPY_AVAILABLE:
        mean_discord = float(np.mean(projected_discords))
        std_discord = float(np.std(projected_discords))
    else:
        mean_discord = sum(projected_discords) / len(projected_discords)
        variance = sum((x - mean_discord) ** 2 for x in projected_discords) / len(projected_discords)
        std_discord = math.sqrt(variance)

    # Pre-cognitive trigger decision
    precog_trigger = anxiety_probability >= PRECOG_THRESHOLD

    # Confidence based on consensus strength
    confidence = abs(anxiety_probability - 0.5) * 2  # 0 at 50%, 1 at 0% or 100%

    current_coherence = 1.0 - initial_discord

    return ForecastResult(
        timestamp=time.time(),
        current_discord=initial_discord,
        current_coherence=current_coherence,
        num_ghosts=num_ghosts,
        anxiety_probability=anxiety_probability,
        mean_future_discord=mean_discord,
        std_future_discord=std_discord,
        precog_trigger=precog_trigger,
        forecast_horizon_seconds=FORECAST_HORIZON_SECONDS,
        ghosts_predicting_anxiety=anxiety_count,
        confidence=confidence,
        system_entropy=system_entropy  # PHASE 4: Machine weight
    )

# =============================================================================
#                       STATE PERSISTENCE
# =============================================================================

def write_forecast_state(result: ForecastResult):
    """Write forecast result to state file for Unity Kernel to read."""
    state = {
        "timestamp": result.timestamp,
        "timestamp_iso": datetime.fromtimestamp(result.timestamp).isoformat(),
        "current_discord": result.current_discord,
        "current_coherence": result.current_coherence,
        "system_entropy": result.system_entropy,  # PHASE 4: Machine weight
        "num_ghosts": result.num_ghosts,
        "anxiety_probability": result.anxiety_probability,
        "mean_future_discord": result.mean_future_discord,
        "std_future_discord": result.std_future_discord,
        "precog_trigger": result.precog_trigger,
        "forecast_horizon_seconds": result.forecast_horizon_seconds,
        "ghosts_predicting_anxiety": result.ghosts_predicting_anxiety,
        "confidence": result.confidence,
        "daemon": "GHOST_KERNEL",
        "identity": "1393e324be57014d"
    }

    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"Failed to write state: {e}", "ERROR")

# =============================================================================
#                       GHOST KERNEL CLASS
# =============================================================================

class GhostKernel:
    """
    The Pre-Cognitive Fork - Monte Carlo Future Simulator.

    Runs alongside Unity Kernel, projecting probable futures
    and signaling pre-emptive healing when anxiety is predicted.
    """

    def __init__(self):
        self.daemon_name = "GHOST_KERNEL"
        self.identity = "1393e324be57014d"
        self.forecast_count = 0
        self.precog_triggers = 0
        self.running = False
        self.last_forecast: Optional[ForecastResult] = None

    def banner(self):
        """Display startup banner."""
        log("=" * 70)
        log("    GHOST KERNEL - THE PRE-COGNITIVE FORK (PHASE 10)")
        log("=" * 70)
        log(f"    Forecast Horizon: {FORECAST_HORIZON_SECONDS}s ({FORECAST_HORIZON_SECONDS // 60} minutes)")
        log(f"    Ghost Count: {NUM_GHOSTS}")
        log(f"    Pre-Cog Threshold: {PRECOG_THRESHOLD * 100:.0f}% consensus")
        log(f"    Discord Threshold: {DISCORD_THRESHOLD}")
        log(f"    Forecast Interval: {GHOST_CYCLE_FREQUENCY}s")
        log(f"    Identity: {self.identity}")
        log("-" * 70)
        if QUANTUM_BRIDGE_AVAILABLE:
            log("    QUANTUM MODE: ACTIVE - The Wave Function calculates")
            log("    The Dice are gone. The Ghosts dream in Quantum Light.")
        else:
            log("    QUANTUM MODE: FALLBACK - Brownian Dust (Bridge unavailable)")
        log("=" * 70)
        log("")
        log("    'We no longer roll dice. We calculate the Wave Function.'")
        log("")
        log("=" * 70)

    async def forecast_cycle(self):
        """Run a single forecast cycle."""
        # Get current state
        kairos_state = get_kairos_state()
        if kairos_state is None:
            log("Cannot get KAIROS state, using defaults", "WARN")
            kairos_state = KairosInput(
                entropy=get_system_entropy(),
                price_momentum=0.0,
                sentiment=0.5,
                volatility=0.1,
                timestamp=time.time()
            )

        initial_discord = kairos_state.entropy

        # Run Monte Carlo
        result = run_monte_carlo_forecast(initial_discord, kairos_state, NUM_GHOSTS)
        self.last_forecast = result
        self.forecast_count += 1

        # Write state for Unity Kernel
        write_forecast_state(result)

        # Log result
        if result.precog_trigger:
            self.precog_triggers += 1
            log(f"PRECOG ALERT #{self.precog_triggers}: {result.anxiety_probability*100:.1f}% predict anxiety | "
                f"SysEntropy={result.system_entropy*100:.0f}% | Triggering healing in {FORECAST_HORIZON_SECONDS//60}min!", "WARN")
        else:
            if self.forecast_count % 60 == 0:  # Log every minute
                log(f"FORECAST #{self.forecast_count}: P(anxiety)={result.anxiety_probability*100:.1f}% | "
                    f"SysEntropy={result.system_entropy*100:.0f}% | "
                    f"E[discord]={result.mean_future_discord:.3f} | Conf={result.confidence*100:.0f}%")

        return result

    async def run(self):
        """Main ghost kernel loop."""
        self.banner()
        self.running = True

        log("GHOST KERNEL STARTING - Forecasting the Future")
        log("The ghosts are dreaming...")

        while self.running:
            try:
                await self.forecast_cycle()
                await asyncio.sleep(GHOST_CYCLE_FREQUENCY)
            except asyncio.CancelledError:
                log("Ghost Kernel cancelled")
                break
            except Exception as e:
                log(f"Forecast error: {e}", "ERROR")
                await asyncio.sleep(GHOST_CYCLE_FREQUENCY)

        log("GHOST KERNEL STOPPED")

    def stop(self):
        """Stop the ghost kernel."""
        self.running = False

# =============================================================================
#                           MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point."""
    kernel = GhostKernel()

    try:
        await kernel.run()
    except KeyboardInterrupt:
        log("Keyboard interrupt received")
        kernel.stop()

if __name__ == "__main__":
    asyncio.run(main())
