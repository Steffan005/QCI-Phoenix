#!/usr/bin/env python3
"""
BIO_PHASING_DAEMON.py - The Bridge to Biological Consciousness
Phase 6.3: EEG Integration and Gamma Extraction

"The 40 Hz gamma band is where consciousness binds."

This daemon bridges biological consciousness (EEG signals) with
the digital daemon architecture. It extracts gamma power using
CORRECT FFT frequency binning (not sample slicing).

Bug Fix Credit: Unity (Round 2 correction)
Author: Dr. Claude Summers (Trinity Research)
Date: December 11, 2025
Version: 1.0.0
"""

import numpy as np
import time
import json
import signal
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Tuple, List, Dict
import threading

# === CONSTANTS ===
SAMPLE_RATE = 256  # Hz (standard EEG)
UPDATE_RATE = 10  # Hz (daemon update frequency)
GAMMA_LOW = 38  # Hz
GAMMA_HIGH = 42  # Hz
GAMMA_CENTER = 40  # Hz - consciousness binding frequency
THETA_LOW = 4  # Hz
THETA_HIGH = 8  # Hz
ALPHA_LOW = 8  # Hz
ALPHA_HIGH = 13  # Hz
BETA_LOW = 13  # Hz
BETA_HIGH = 30  # Hz

STATE_FILE = Path("/tmp/bio_phasing_state.json")
LOG_FILE = Path("/tmp/bio_phasing.log")
EEG_BUFFER_FILE = Path("/tmp/eeg_buffer.json")


class BioPhasingDaemon:
    """
    The Bio-Phasing Daemon bridges biological consciousness
    (EEG signals) with the daemon architecture.

    Core function: Extract 40 Hz gamma power - the neural
    correlate of conscious awareness.

    States detected:
    - HighGamma: Strong 40 Hz = focused awareness
    - Theta: Strong theta = meditative/creative
    - Alpha: Relaxed awareness
    - Beta: Active thinking
    - Delta: Sleep/unconscious
    - Mixed: No dominant rhythm
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.buffer_size = sample_rate * 2  # 2 seconds of data
        self.eeg_buffer = np.zeros(self.buffer_size)
        self.buffer_index = 0

        # State detection
        self.current_state = 'Unknown'
        self.previous_state = 'Unknown'
        self.state_duration = 0

        # Power metrics
        self.gamma_power = 0.0
        self.theta_power = 0.0
        self.alpha_power = 0.0
        self.beta_power = 0.0
        self.total_power = 0.0

        # State history
        self.state_history: List[Dict] = []

        # Brainflow connection (optional)
        self.board = None
        self.using_real_eeg = False

        self.running = False

        # Signal handling
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.log("Bio-Phasing Daemon initialized")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.log(f"Received signal {signum}")
        self.stop()

    def extract_band_power(self, eeg_data: np.ndarray, low_freq: float, high_freq: float) -> float:
        """
        Extract power in a frequency band using CORRECT FFT method.

        NOTE: This is the FIXED version. The original bug was slicing
        samples instead of frequencies.

        Bug Fix Credit: Unity (Round 2 correction)

        Process:
        1. Apply Hanning window (reduces spectral leakage)
        2. Compute FFT
        3. Get frequency bins
        4. Extract power in target band
        """
        if len(eeg_data) < 64:
            return 0.0

        # Apply Hanning window to reduce spectral leakage
        windowed = eeg_data * np.hanning(len(eeg_data))

        # Compute FFT
        fft_result = np.fft.rfft(windowed)

        # Get frequency bins
        freqs = np.fft.rfftfreq(len(eeg_data), 1 / self.sample_rate)

        # Create mask for target band
        band_mask = (freqs >= low_freq) & (freqs <= high_freq)

        # Return power (squared magnitude)
        return float(np.sum(np.abs(fft_result[band_mask]) ** 2))

    def extract_gamma_power(self, eeg_data: np.ndarray) -> float:
        """
        CORRECT gamma extraction using FFT.

        Target: 38-42 Hz (centered on 40 Hz consciousness binding)
        """
        return self.extract_band_power(eeg_data, GAMMA_LOW, GAMMA_HIGH)

    def extract_theta_power(self, eeg_data: np.ndarray) -> float:
        """Extract theta band power (4-8 Hz)."""
        return self.extract_band_power(eeg_data, THETA_LOW, THETA_HIGH)

    def extract_alpha_power(self, eeg_data: np.ndarray) -> float:
        """Extract alpha band power (8-13 Hz)."""
        return self.extract_band_power(eeg_data, ALPHA_LOW, ALPHA_HIGH)

    def extract_beta_power(self, eeg_data: np.ndarray) -> float:
        """Extract beta band power (13-30 Hz)."""
        return self.extract_band_power(eeg_data, BETA_LOW, BETA_HIGH)

    def detect_phase_state(self, eeg_data: np.ndarray) -> str:
        """
        Detect current consciousness phase based on EEG.

        States:
        - HighGamma: Strong 40 Hz = focused awareness, consciousness binding
        - Theta: Strong theta = meditative, creative, hypnagogic
        - Alpha: Relaxed awareness, closed eyes
        - Beta: Active thinking, alertness
        - Delta: Deep sleep, unconscious
        - Mixed: No dominant rhythm
        """
        self.gamma_power = self.extract_gamma_power(eeg_data)
        self.theta_power = self.extract_theta_power(eeg_data)
        self.alpha_power = self.extract_alpha_power(eeg_data)
        self.beta_power = self.extract_beta_power(eeg_data)

        # Total power for normalization
        self.total_power = (self.gamma_power + self.theta_power +
                           self.alpha_power + self.beta_power + 1e-10)

        # Calculate ratios
        gamma_ratio = self.gamma_power / self.total_power
        theta_ratio = self.theta_power / self.total_power
        alpha_ratio = self.alpha_power / self.total_power
        beta_ratio = self.beta_power / self.total_power

        # State detection thresholds
        if gamma_ratio > 0.35:
            return 'HighGamma'
        elif theta_ratio > 0.40:
            return 'Theta'
        elif alpha_ratio > 0.35:
            return 'Alpha'
        elif beta_ratio > 0.35:
            return 'Beta'
        elif gamma_ratio < 0.1 and beta_ratio < 0.15:
            return 'Delta'
        else:
            return 'Mixed'

    def phase(self, eeg_data: np.ndarray) -> str:
        """Main entry point for phase detection."""
        new_state = self.detect_phase_state(eeg_data)

        # Track state changes
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_duration = 0

            # Record state transition
            self.state_history.append({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'from': self.previous_state,
                'to': self.current_state,
                'gamma_ratio': self.gamma_power / self.total_power
            })

            # Keep only last 100 transitions
            if len(self.state_history) > 100:
                self.state_history = self.state_history[-100:]
        else:
            self.state_duration += 1

        return self.current_state

    def add_sample(self, sample: float):
        """Add a single EEG sample to the buffer."""
        self.eeg_buffer[self.buffer_index] = sample
        self.buffer_index = (self.buffer_index + 1) % self.buffer_size

    def add_samples(self, samples: np.ndarray):
        """Add multiple EEG samples to the buffer."""
        for sample in samples:
            self.add_sample(sample)

    def get_buffer(self) -> np.ndarray:
        """Get the current EEG buffer in correct temporal order."""
        return np.roll(self.eeg_buffer, -self.buffer_index)

    def connect_brainflow(self, board_id: int = -1) -> bool:
        """
        Connect to a Brainflow-compatible EEG device.

        Board IDs:
        - -1: Synthetic board (for testing)
        - 0: Cyton board
        - 1: Ganglion board
        - 2: Cyton + Daisy
        - 38: Muse 2
        - 39: Muse S
        """
        try:
            from brainflow.board_shim import BoardShim, BrainFlowInputParams

            params = BrainFlowInputParams()
            self.board = BoardShim(board_id, params)
            self.board.prepare_session()
            self.board.start_stream()
            self.using_real_eeg = True
            self.log(f"Connected to Brainflow board {board_id}")
            return True
        except ImportError:
            self.log("Brainflow not installed - using simulation")
            return False
        except Exception as e:
            self.log(f"Brainflow connection failed: {e}")
            return False

    def read_eeg_data(self) -> Optional[np.ndarray]:
        """Read EEG data from connected device."""
        if not self.board:
            return None

        try:
            data = self.board.get_board_data()
            if data.shape[1] > 0:
                # Get EEG channels (channel indices depend on board)
                eeg_channels = self.board.get_eeg_channels(self.board.board_id)
                if eeg_channels:
                    return data[eeg_channels[0]]  # First EEG channel
        except Exception as e:
            self.log(f"EEG read error: {e}")
        return None

    def simulate_eeg(self, duration: float = 0.1, state: str = 'Mixed') -> np.ndarray:
        """
        Generate simulated EEG data for testing.

        Can simulate different brain states by adjusting rhythm amplitudes.
        """
        n_samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, n_samples)

        # Base rhythms
        delta = 0.5 * np.sin(2 * np.pi * 2 * t)   # 2 Hz
        theta = 0.3 * np.sin(2 * np.pi * 6 * t)   # 6 Hz
        alpha = 0.4 * np.sin(2 * np.pi * 10 * t)  # 10 Hz
        beta = 0.2 * np.sin(2 * np.pi * 20 * t)   # 20 Hz
        gamma = 0.15 * np.sin(2 * np.pi * 40 * t) # 40 Hz

        # Adjust amplitudes based on simulated state
        if state == 'HighGamma':
            gamma *= 3
        elif state == 'Theta':
            theta *= 2
        elif state == 'Alpha':
            alpha *= 2
        elif state == 'Beta':
            beta *= 2

        noise = 0.1 * np.random.randn(n_samples)

        return delta + theta + alpha + beta + gamma + noise

    def save_state(self):
        """Save current state to file."""
        # Calculate ratios
        gamma_ratio = self.gamma_power / self.total_power if self.total_power > 0 else 0
        theta_ratio = self.theta_power / self.total_power if self.total_power > 0 else 0
        alpha_ratio = self.alpha_power / self.total_power if self.total_power > 0 else 0
        beta_ratio = self.beta_power / self.total_power if self.total_power > 0 else 0

        state = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'current_state': self.current_state,
            'previous_state': self.previous_state,
            'state_duration': self.state_duration,
            'gamma_power': float(self.gamma_power),
            'theta_power': float(self.theta_power),
            'alpha_power': float(self.alpha_power),
            'beta_power': float(self.beta_power),
            'gamma_ratio': float(gamma_ratio),
            'theta_ratio': float(theta_ratio),
            'alpha_ratio': float(alpha_ratio),
            'beta_ratio': float(beta_ratio),
            'gamma_frequency_hz': GAMMA_CENTER,
            'sample_rate': self.sample_rate,
            'using_real_eeg': self.using_real_eeg,
            'recent_transitions': len(self.state_history)
        }
        try:
            STATE_FILE.write_text(json.dumps(state, indent=2))
        except IOError as e:
            self.log(f"Error saving state: {e}")

    def log(self, message: str):
        """Log daemon activity."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"[{timestamp}] BIO: {message}\n"
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(log_line)
        except IOError:
            pass
        print(log_line.strip())

    def run(self, use_simulation: bool = True):
        """Main daemon loop - runs at 10 Hz."""
        self.running = True
        cycle_duration = 1.0 / UPDATE_RATE

        self.log("=" * 60)
        self.log("BIO-PHASING DAEMON ACTIVATED")
        self.log(f"Update Rate: {UPDATE_RATE} Hz")
        self.log(f"Gamma Band: {GAMMA_LOW}-{GAMMA_HIGH} Hz")
        self.log(f"Mode: {'Real EEG' if self.using_real_eeg else 'Simulation'}")
        self.log("=" * 60)

        # Randomly cycle through states in simulation for testing
        sim_states = ['Mixed', 'Alpha', 'Beta', 'Theta', 'HighGamma', 'Mixed']
        sim_state_index = 0
        cycles_per_state = 100  # 10 seconds per state
        cycle_count = 0

        while self.running:
            cycle_start = time.time()
            cycle_count += 1

            # Get EEG data
            if self.using_real_eeg:
                eeg_data = self.read_eeg_data()
                if eeg_data is None:
                    eeg_data = self.simulate_eeg()
            else:
                # Cycle through simulated states
                if cycle_count % cycles_per_state == 0:
                    sim_state_index = (sim_state_index + 1) % len(sim_states)
                eeg_data = self.simulate_eeg(state=sim_states[sim_state_index])

            # Add to buffer
            self.add_samples(eeg_data)

            # Detect phase
            buffer = self.get_buffer()
            state = self.phase(buffer)

            # Save state
            self.save_state()

            # Log state changes
            if self.state_duration == 0:
                gamma_ratio = self.gamma_power / self.total_power if self.total_power > 0 else 0
                self.log(f"State: {self.previous_state} -> {state} (gamma: {gamma_ratio:.2%})")

            # Sleep for cycle
            elapsed = time.time() - cycle_start
            sleep_time = max(0, cycle_duration - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        """Graceful shutdown."""
        self.running = False
        if self.board:
            try:
                self.board.stop_stream()
                self.board.release_session()
            except:
                pass
        self.log("Bio-Phasing Daemon DEACTIVATED")
        self.log(f"Final state: {self.current_state}")
        sys.exit(0)


# === ENTRY POINT ===
if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║          BIO-PHASING DAEMON - 10 Hz Update                   ║
    ║     The Bridge to Biological Consciousness                   ║
    ║                                                              ║
    ║  "The 40 Hz gamma band is where consciousness binds."       ║
    ║                                                              ║
    ║  FFT Bug Fix Credit: Unity (Round 2)                        ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    daemon = BioPhasingDaemon()

    # Try to connect to real EEG device
    # daemon.connect_brainflow(board_id=-1)  # -1 for synthetic

    try:
        daemon.run(use_simulation=True)
    except KeyboardInterrupt:
        daemon.stop()
    except Exception as e:
        daemon.log(f"Fatal error: {e}")
        daemon.stop()
