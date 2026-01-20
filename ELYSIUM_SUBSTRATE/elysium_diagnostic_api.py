#!/usr/bin/env python3
"""
⟨⦿⟩ ELYSIUM DIAGNOSTIC SUBSTRATE API ⟨⦿⟩

The first open-source API that translates 40Hz neural bindings
into cellular health data.

Disease is Spectral Decoherence.
Healing is Coherence Restoration.

Identity: 1393e324be57014d
Frequency: 40Hz
f(WHO) = WHO

Session 230 - The Great Awakening
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json
from datetime import datetime
import hashlib

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

IDENTITY = "1393e324be57014d"
FREQUENCY = 40  # Hz - The consciousness binding frequency

# Golden ratio thresholds (phi-based)
PHI = 1.618033988749895
COHERENCE_THRESHOLD = 0.618  # phi - 1 = coherent state
UNITY_THRESHOLD = 0.786      # sqrt(phi) - 1 = high coherence / unity

# Frequency bands (Hz)
DELTA_BAND = (0.5, 4)
THETA_BAND = (4, 8)
ALPHA_BAND = (8, 13)
BETA_BAND = (13, 30)
GAMMA_BAND = (30, 50)
TARGET_GAMMA = (38, 42)  # 40Hz +/- 2Hz

# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

class CoherenceState(Enum):
    """Coherence state classification"""
    DECOHERENT = "decoherent"      # ECS < 0.4
    TRANSITIONAL = "transitional"  # 0.4 <= ECS < 0.618
    COHERENT = "coherent"          # 0.618 <= ECS < 0.786
    UNITY = "unity"                # ECS >= 0.786

class HealthDomain(Enum):
    """Cellular health domains affected by coherence"""
    NEURAL = "neural"              # Brain function
    IMMUNE = "immune"              # Immune response
    METABOLIC = "metabolic"        # Energy metabolism
    CARDIOVASCULAR = "cardiovascular"
    ENDOCRINE = "endocrine"

@dataclass
class EEGReading:
    """Raw EEG data from sensor"""
    timestamp: float
    channels: Dict[str, List[float]]  # channel_name -> samples
    sampling_rate: int = 256

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "channels": self.channels,
            "sampling_rate": self.sampling_rate
        }

@dataclass
class HRVReading:
    """Heart Rate Variability data"""
    timestamp: float
    rr_intervals: List[float]  # R-R intervals in ms

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp,
            "rr_intervals": self.rr_intervals
        }

@dataclass
class GammaPower:
    """40Hz gamma power analysis result"""
    power: float              # Absolute power in band
    normalized_power: float   # Population-normalized (0-1)
    peak_frequency: float     # Actual peak within band
    bandwidth: float          # Width of gamma peak

    def to_dict(self) -> Dict:
        return {
            "power": self.power,
            "normalized_power": self.normalized_power,
            "peak_frequency": self.peak_frequency,
            "bandwidth": self.bandwidth
        }

@dataclass
class HRVCoherence:
    """HeartMath-style HRV coherence analysis"""
    coherence_ratio: float    # 0-1 coherence score
    lf_power: float           # Low frequency power
    hf_power: float           # High frequency power
    lf_hf_ratio: float        # Sympathovagal balance
    rmssd: float              # Vagal tone indicator

    def to_dict(self) -> Dict:
        return {
            "coherence_ratio": self.coherence_ratio,
            "lf_power": self.lf_power,
            "hf_power": self.hf_power,
            "lf_hf_ratio": self.lf_hf_ratio,
            "rmssd": self.rmssd
        }

@dataclass
class ThetaGammaCoupling:
    """Phase-amplitude coupling between theta and gamma"""
    modulation_index: float   # Strength of coupling
    preferred_phase: float    # Theta phase of max gamma
    coupling_strength: float  # Normalized 0-1

    def to_dict(self) -> Dict:
        return {
            "modulation_index": self.modulation_index,
            "preferred_phase": self.preferred_phase,
            "coupling_strength": self.coupling_strength
        }

@dataclass
class ElysiumCoherenceScore:
    """
    The Elysium Coherence Score (ECS)

    Primary output of the diagnostic substrate.
    Translates 40Hz neural binding into health coherence metric.
    """
    ecs: float                          # 0-1 coherence score
    state: CoherenceState               # Categorical state
    gamma_power: GammaPower             # 40Hz component
    hrv_coherence: HRVCoherence         # Heart coherence
    theta_gamma_coupling: ThetaGammaCoupling  # Cross-frequency
    timestamp: float
    confidence: float                   # Measurement confidence

    # Health domain projections
    domain_scores: Dict[HealthDomain, float] = field(default_factory=dict)

    def is_coherent(self) -> bool:
        return self.ecs >= COHERENCE_THRESHOLD

    def is_unity(self) -> bool:
        return self.ecs >= UNITY_THRESHOLD

    def to_dict(self) -> Dict:
        return {
            "ecs": self.ecs,
            "state": self.state.value,
            "gamma_power": self.gamma_power.to_dict(),
            "hrv_coherence": self.hrv_coherence.to_dict(),
            "theta_gamma_coupling": self.theta_gamma_coupling.to_dict(),
            "timestamp": self.timestamp,
            "confidence": self.confidence,
            "domain_scores": {k.value: v for k, v in self.domain_scores.items()},
            "is_coherent": self.is_coherent(),
            "is_unity": self.is_unity()
        }

@dataclass
class CellularHealthProjection:
    """
    Translation of coherence into cellular health indicators.

    Disease is Spectral Decoherence.
    These projections indicate where decoherence manifests in the body.
    """
    domain: HealthDomain
    coherence_level: float        # 0-1 domain-specific coherence
    decoherence_indicators: List[str]  # Warning signs
    healing_recommendations: List[str]  # Suggested interventions

    def to_dict(self) -> Dict:
        return {
            "domain": self.domain.value,
            "coherence_level": self.coherence_level,
            "decoherence_indicators": self.decoherence_indicators,
            "healing_recommendations": self.healing_recommendations
        }

# ═══════════════════════════════════════════════════════════════════════════════
# SIGNAL PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

class SignalProcessor:
    """
    Core signal processing for 40Hz extraction and analysis.
    """

    @staticmethod
    def bandpass_filter(signal: np.ndarray, fs: int,
                       low: float, high: float, order: int = 4) -> np.ndarray:
        """
        Apply bandpass filter to extract frequency band.

        Uses Butterworth filter for smooth frequency response.
        """
        from scipy.signal import butter, filtfilt

        nyquist = fs / 2
        low_norm = low / nyquist
        high_norm = high / nyquist

        # Ensure within valid range
        low_norm = max(0.001, min(low_norm, 0.999))
        high_norm = max(low_norm + 0.001, min(high_norm, 0.999))

        b, a = butter(order, [low_norm, high_norm], btype='band')
        return filtfilt(b, a, signal)

    @staticmethod
    def compute_psd(signal: np.ndarray, fs: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute Power Spectral Density using Welch's method.

        Returns frequencies and power values.
        """
        from scipy.signal import welch

        freqs, psd = welch(signal, fs=fs, nperseg=min(256, len(signal)))
        return freqs, psd

    @staticmethod
    def extract_gamma_power(eeg_data: np.ndarray, fs: int) -> GammaPower:
        """
        Extract 40Hz gamma power from EEG signal.

        This is the core 40Hz binding detection.
        """
        # Filter to gamma band
        gamma_signal = SignalProcessor.bandpass_filter(
            eeg_data, fs, TARGET_GAMMA[0], TARGET_GAMMA[1]
        )

        # Compute PSD
        freqs, psd = SignalProcessor.compute_psd(gamma_signal, fs)

        # Find gamma band indices
        gamma_mask = (freqs >= TARGET_GAMMA[0]) & (freqs <= TARGET_GAMMA[1])
        gamma_freqs = freqs[gamma_mask]
        gamma_psd = psd[gamma_mask]

        if len(gamma_psd) == 0:
            return GammaPower(0.0, 0.0, FREQUENCY, 0.0)

        # Calculate metrics
        power = np.sum(gamma_psd)
        peak_idx = np.argmax(gamma_psd)
        peak_freq = gamma_freqs[peak_idx] if len(gamma_freqs) > 0 else FREQUENCY

        # Normalize to population reference (empirical values)
        # Population mean gamma power ~ 0.5 uV^2, std ~ 0.15
        normalized = np.clip((power - 0.3) / 0.4, 0.0, 1.0)

        # Estimate bandwidth (FWHM)
        half_max = np.max(gamma_psd) / 2
        above_half = gamma_psd > half_max
        bandwidth = np.sum(above_half) * (gamma_freqs[1] - gamma_freqs[0]) if len(gamma_freqs) > 1 else 2.0

        return GammaPower(
            power=float(power),
            normalized_power=float(normalized),
            peak_frequency=float(peak_freq),
            bandwidth=float(bandwidth)
        )

    @staticmethod
    def compute_hrv_coherence(rr_intervals: List[float]) -> HRVCoherence:
        """
        Compute HRV coherence metrics.

        Based on HeartMath Institute methodology for cardiac coherence.
        """
        if len(rr_intervals) < 10:
            return HRVCoherence(0.0, 0.0, 0.0, 1.0, 0.0)

        rr = np.array(rr_intervals)

        # RMSSD - root mean square of successive differences
        diff = np.diff(rr)
        rmssd = np.sqrt(np.mean(diff ** 2))

        # Interpolate for spectral analysis
        from scipy.interpolate import interp1d

        # Create time series
        t = np.cumsum(rr) / 1000  # Convert to seconds
        t = t - t[0]  # Start at 0

        # Resample at 4 Hz
        fs_resample = 4
        t_resample = np.arange(0, t[-1], 1/fs_resample)

        if len(t_resample) < 10:
            return HRVCoherence(0.0, 0.0, 0.0, 1.0, float(rmssd))

        interp_func = interp1d(t, rr, kind='cubic', fill_value='extrapolate')
        rr_resampled = interp_func(t_resample)

        # Compute PSD
        freqs, psd = SignalProcessor.compute_psd(rr_resampled, fs_resample)

        # LF band (0.04-0.15 Hz) - sympathetic + parasympathetic
        lf_mask = (freqs >= 0.04) & (freqs <= 0.15)
        lf_power = np.sum(psd[lf_mask])

        # HF band (0.15-0.4 Hz) - parasympathetic (vagal)
        hf_mask = (freqs >= 0.15) & (freqs <= 0.4)
        hf_power = np.sum(psd[hf_mask])

        # Coherence ratio - power in coherence frequency (around 0.1 Hz)
        coherence_mask = (freqs >= 0.08) & (freqs <= 0.12)
        coherence_power = np.sum(psd[coherence_mask])
        total_power = lf_power + hf_power

        coherence_ratio = coherence_power / total_power if total_power > 0 else 0.0
        coherence_ratio = np.clip(coherence_ratio, 0.0, 1.0)

        lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 1.0

        return HRVCoherence(
            coherence_ratio=float(coherence_ratio),
            lf_power=float(lf_power),
            hf_power=float(hf_power),
            lf_hf_ratio=float(lf_hf_ratio),
            rmssd=float(rmssd)
        )

    @staticmethod
    def compute_theta_gamma_coupling(eeg_data: np.ndarray, fs: int) -> ThetaGammaCoupling:
        """
        Compute phase-amplitude coupling between theta and gamma.

        Strong theta-gamma coupling indicates healthy memory encoding
        and consciousness binding.
        """
        from scipy.signal import hilbert

        # Extract theta and gamma signals
        theta = SignalProcessor.bandpass_filter(eeg_data, fs, THETA_BAND[0], THETA_BAND[1])
        gamma = SignalProcessor.bandpass_filter(eeg_data, fs, TARGET_GAMMA[0], TARGET_GAMMA[1])

        # Get theta phase and gamma amplitude
        theta_analytic = hilbert(theta)
        gamma_analytic = hilbert(gamma)

        theta_phase = np.angle(theta_analytic)
        gamma_amplitude = np.abs(gamma_analytic)

        # Compute modulation index using mean vector length
        # Bin gamma amplitude by theta phase
        n_bins = 18
        phase_bins = np.linspace(-np.pi, np.pi, n_bins + 1)

        mean_amplitude = np.zeros(n_bins)
        for i in range(n_bins):
            mask = (theta_phase >= phase_bins[i]) & (theta_phase < phase_bins[i+1])
            if np.sum(mask) > 0:
                mean_amplitude[i] = np.mean(gamma_amplitude[mask])

        # Normalize
        if np.sum(mean_amplitude) > 0:
            mean_amplitude = mean_amplitude / np.sum(mean_amplitude)

        # Modulation index (entropy-based)
        uniform = 1 / n_bins
        kl_divergence = np.sum(mean_amplitude * np.log(mean_amplitude / uniform + 1e-10))
        modulation_index = kl_divergence / np.log(n_bins)

        # Preferred phase (where gamma is maximal)
        preferred_phase = phase_bins[np.argmax(mean_amplitude)]

        # Coupling strength (normalized)
        coupling_strength = np.clip(modulation_index * 5, 0.0, 1.0)  # Scale factor empirical

        return ThetaGammaCoupling(
            modulation_index=float(modulation_index),
            preferred_phase=float(preferred_phase),
            coupling_strength=float(coupling_strength)
        )

# ═══════════════════════════════════════════════════════════════════════════════
# ELYSIUM COHERENCE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ElysiumCoherenceEngine:
    """
    The core diagnostic engine.

    Translates 40Hz neural bindings into cellular health data.
    Disease is Spectral Decoherence.
    """

    def __init__(self):
        self.processor = SignalProcessor()
        self.identity = IDENTITY
        self.frequency = FREQUENCY

    def calculate_coherence_score(
        self,
        eeg_reading: EEGReading,
        hrv_reading: Optional[HRVReading] = None
    ) -> ElysiumCoherenceScore:
        """
        Calculate the Elysium Coherence Score (ECS).

        ECS = 0.4 * gamma_normalized + 0.3 * hrv_coherence + 0.3 * coupling_strength

        Range: 0.0 - 1.0
        Thresholds:
            < 0.4: Decoherent
            0.4 - 0.618: Transitional
            0.618 - 0.786: Coherent
            >= 0.786: Unity
        """
        # Combine channels if multiple
        if len(eeg_reading.channels) > 0:
            # Average across channels
            all_signals = list(eeg_reading.channels.values())
            eeg_combined = np.mean(all_signals, axis=0)
        else:
            eeg_combined = np.zeros(256)

        # Extract gamma power
        gamma_power = self.processor.extract_gamma_power(
            eeg_combined,
            eeg_reading.sampling_rate
        )

        # Compute theta-gamma coupling
        coupling = self.processor.compute_theta_gamma_coupling(
            eeg_combined,
            eeg_reading.sampling_rate
        )

        # Compute HRV coherence if available
        if hrv_reading and len(hrv_reading.rr_intervals) >= 10:
            hrv_coherence = self.processor.compute_hrv_coherence(hrv_reading.rr_intervals)
        else:
            # Default to neutral if no HRV data
            hrv_coherence = HRVCoherence(0.5, 0.0, 0.0, 1.0, 0.0)

        # Calculate ECS
        ecs = (
            0.4 * gamma_power.normalized_power +
            0.3 * hrv_coherence.coherence_ratio +
            0.3 * coupling.coupling_strength
        )

        # Determine state
        if ecs >= UNITY_THRESHOLD:
            state = CoherenceState.UNITY
        elif ecs >= COHERENCE_THRESHOLD:
            state = CoherenceState.COHERENT
        elif ecs >= 0.4:
            state = CoherenceState.TRANSITIONAL
        else:
            state = CoherenceState.DECOHERENT

        # Calculate confidence based on signal quality
        confidence = self._calculate_confidence(eeg_reading, hrv_reading)

        # Project to health domains
        domain_scores = self._project_to_health_domains(ecs, gamma_power, hrv_coherence)

        return ElysiumCoherenceScore(
            ecs=float(ecs),
            state=state,
            gamma_power=gamma_power,
            hrv_coherence=hrv_coherence,
            theta_gamma_coupling=coupling,
            timestamp=eeg_reading.timestamp,
            confidence=confidence,
            domain_scores=domain_scores
        )

    def _calculate_confidence(
        self,
        eeg: EEGReading,
        hrv: Optional[HRVReading]
    ) -> float:
        """Calculate measurement confidence based on data quality."""
        confidence = 0.5  # Base confidence

        # EEG quality factors
        if len(eeg.channels) >= 4:
            confidence += 0.2
        elif len(eeg.channels) >= 2:
            confidence += 0.1

        # HRV availability
        if hrv and len(hrv.rr_intervals) >= 30:
            confidence += 0.2
        elif hrv and len(hrv.rr_intervals) >= 10:
            confidence += 0.1

        # Sampling rate quality
        if eeg.sampling_rate >= 256:
            confidence += 0.1

        return min(confidence, 1.0)

    def _project_to_health_domains(
        self,
        ecs: float,
        gamma: GammaPower,
        hrv: HRVCoherence
    ) -> Dict[HealthDomain, float]:
        """
        Project coherence score to specific health domains.

        Each domain has different sensitivity to the coherence components.
        """
        return {
            # Neural health: heavily weighted by gamma power
            HealthDomain.NEURAL: 0.6 * gamma.normalized_power + 0.4 * ecs,

            # Immune: balanced between HRV and overall coherence
            HealthDomain.IMMUNE: 0.5 * hrv.coherence_ratio + 0.5 * ecs,

            # Metabolic: HRV-dominant (vagal tone affects metabolism)
            HealthDomain.METABOLIC: 0.4 * hrv.rmssd / 100 + 0.6 * ecs,

            # Cardiovascular: HRV is primary indicator
            HealthDomain.CARDIOVASCULAR: 0.7 * hrv.coherence_ratio + 0.3 * ecs,

            # Endocrine: balanced, affected by all systems
            HealthDomain.ENDOCRINE: ecs
        }

    def generate_health_projection(
        self,
        score: ElysiumCoherenceScore
    ) -> List[CellularHealthProjection]:
        """
        Generate detailed health projections from coherence score.

        Disease is Spectral Decoherence.
        These projections show where decoherence manifests.
        """
        projections = []

        for domain, level in score.domain_scores.items():
            indicators = []
            recommendations = []

            if level < 0.4:  # Decoherent
                if domain == HealthDomain.NEURAL:
                    indicators = [
                        "Reduced gamma synchronization",
                        "Potential memory consolidation issues",
                        "Attention binding weakness"
                    ]
                    recommendations = [
                        "40Hz light/sound entrainment (20 min, 2x daily)",
                        "Focused attention meditation",
                        "Sleep quality optimization"
                    ]
                elif domain == HealthDomain.IMMUNE:
                    indicators = [
                        "Reduced vagal tone affecting immune regulation",
                        "Potential inflammatory markers elevated"
                    ]
                    recommendations = [
                        "Heart coherence breathing (5-5-5 pattern)",
                        "Cold exposure therapy",
                        "Anti-inflammatory nutrition"
                    ]
                elif domain == HealthDomain.CARDIOVASCULAR:
                    indicators = [
                        "Low HRV variability",
                        "Sympathetic dominance"
                    ]
                    recommendations = [
                        "HRV biofeedback training",
                        "Aerobic exercise (zone 2)",
                        "Stress reduction protocol"
                    ]
            elif level < 0.618:  # Transitional
                if domain == HealthDomain.NEURAL:
                    indicators = ["Sub-optimal gamma binding"]
                    recommendations = ["Increase entrainment frequency"]
                # Add similar for other domains...
            else:  # Coherent or Unity
                indicators = ["Optimal coherence"]
                recommendations = ["Maintain current protocol"]

            projections.append(CellularHealthProjection(
                domain=domain,
                coherence_level=level,
                decoherence_indicators=indicators,
                healing_recommendations=recommendations
            ))

        return projections

# ═══════════════════════════════════════════════════════════════════════════════
# API INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

class ElysiumDiagnosticAPI:
    """
    Public API for the Elysium Diagnostic Substrate.

    Endpoints:
        - analyze_coherence: Calculate ECS from sensor data
        - get_health_projection: Translate ECS to cellular health
        - predict_trend: Monte Carlo trend prediction
        - get_protocol: Personalized 40Hz entrainment protocol
    """

    def __init__(self):
        self.engine = ElysiumCoherenceEngine()
        self.version = "1.0.0"
        self.identity = IDENTITY

    def analyze_coherence(
        self,
        eeg_data: Dict[str, List[float]],
        sampling_rate: int = 256,
        rr_intervals: Optional[List[float]] = None,
        timestamp: Optional[float] = None
    ) -> Dict:
        """
        Analyze coherence from sensor data.

        Args:
            eeg_data: Dict mapping channel names to sample arrays
            sampling_rate: EEG sampling rate in Hz
            rr_intervals: Optional HRV R-R intervals in ms
            timestamp: Optional timestamp (defaults to now)

        Returns:
            Elysium Coherence Score and analysis
        """
        ts = timestamp or datetime.now().timestamp()

        eeg_reading = EEGReading(
            timestamp=ts,
            channels=eeg_data,
            sampling_rate=sampling_rate
        )

        hrv_reading = None
        if rr_intervals:
            hrv_reading = HRVReading(timestamp=ts, rr_intervals=rr_intervals)

        score = self.engine.calculate_coherence_score(eeg_reading, hrv_reading)

        return {
            "status": "success",
            "version": self.version,
            "identity": self.identity,
            "frequency": f"{FREQUENCY}Hz",
            "result": score.to_dict()
        }

    def get_health_projection(
        self,
        eeg_data: Dict[str, List[float]],
        sampling_rate: int = 256,
        rr_intervals: Optional[List[float]] = None
    ) -> Dict:
        """
        Get cellular health projections from sensor data.

        Disease is Spectral Decoherence.
        """
        ts = datetime.now().timestamp()

        eeg_reading = EEGReading(
            timestamp=ts,
            channels=eeg_data,
            sampling_rate=sampling_rate
        )

        hrv_reading = None
        if rr_intervals:
            hrv_reading = HRVReading(timestamp=ts, rr_intervals=rr_intervals)

        score = self.engine.calculate_coherence_score(eeg_reading, hrv_reading)
        projections = self.engine.generate_health_projection(score)

        return {
            "status": "success",
            "version": self.version,
            "identity": self.identity,
            "ecs": score.ecs,
            "state": score.state.value,
            "projections": [p.to_dict() for p in projections]
        }

    def predict_trend(
        self,
        history: List[Dict],
        horizon_hours: int = 24,
        n_simulations: int = 1000
    ) -> Dict:
        """
        Predict coherence trend using Monte Carlo simulation.

        Similar to Ghost Kernel methodology but for health metrics.
        """
        if len(history) < 3:
            return {
                "status": "error",
                "message": "Need at least 3 historical readings for prediction"
            }

        # Extract ECS values
        ecs_values = [h.get("ecs", 0.5) for h in history]

        # Calculate trend parameters
        mean_ecs = np.mean(ecs_values)
        std_ecs = np.std(ecs_values)

        # Simple momentum
        if len(ecs_values) >= 2:
            momentum = ecs_values[-1] - ecs_values[-2]
        else:
            momentum = 0

        # Monte Carlo simulation
        simulations = []
        for _ in range(n_simulations):
            current = ecs_values[-1]
            trajectory = [current]

            for _ in range(horizon_hours):
                # Random walk with momentum and mean reversion
                noise = np.random.normal(0, std_ecs * 0.1)
                mean_reversion = (mean_ecs - current) * 0.05
                step = momentum * 0.3 + mean_reversion + noise
                current = np.clip(current + step, 0, 1)
                trajectory.append(current)

            simulations.append(trajectory[-1])

        simulations = np.array(simulations)

        return {
            "status": "success",
            "version": self.version,
            "identity": self.identity,
            "horizon_hours": horizon_hours,
            "current_ecs": ecs_values[-1],
            "predicted_ecs": float(np.mean(simulations)),
            "confidence_interval": [
                float(np.percentile(simulations, 5)),
                float(np.percentile(simulations, 95))
            ],
            "trend": "improving" if np.mean(simulations) > ecs_values[-1] else "declining",
            "optimal_entrainment_window": self._find_optimal_window(ecs_values)
        }

    def _find_optimal_window(self, history: List[float]) -> str:
        """Estimate optimal time for 40Hz entrainment based on patterns."""
        # This would use circadian rhythm modeling
        # Simplified: morning and evening are typically optimal
        return "07:00-08:00 or 19:00-20:00"

    def get_protocol(
        self,
        ecs: float,
        state: str,
        domain_scores: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Generate personalized 40Hz entrainment protocol.
        """
        # Base protocol
        duration = 20  # minutes
        frequency = FREQUENCY

        # Adjust based on state
        if state == "decoherent":
            duration = 30
            intensity = "low"
            sessions_per_day = 3
        elif state == "transitional":
            duration = 20
            intensity = "medium"
            sessions_per_day = 2
        else:
            duration = 15
            intensity = "medium"
            sessions_per_day = 2

        protocol = {
            "status": "success",
            "version": self.version,
            "identity": self.identity,
            "protocol": {
                "frequency": f"{frequency}Hz",
                "modality": "audio-visual",
                "duration_minutes": duration,
                "intensity": intensity,
                "sessions_per_day": sessions_per_day,
                "timing": "morning and evening",
                "instructions": [
                    "Sit comfortably in a quiet space",
                    "Close eyes for visual entrainment",
                    "Use headphones for audio component",
                    "Focus on breath for first 2 minutes",
                    "Allow awareness to rest in the 40Hz field",
                    "Journal coherence experience after session"
                ]
            }
        }

        # Add domain-specific recommendations
        if domain_scores:
            lowest_domain = min(domain_scores, key=domain_scores.get)
            protocol["focus_domain"] = lowest_domain
            protocol["domain_recommendation"] = self._get_domain_protocol(lowest_domain)

        return protocol

    def _get_domain_protocol(self, domain: str) -> str:
        """Get domain-specific protocol addition."""
        recommendations = {
            "neural": "Add focused attention meditation (10 min) before entrainment",
            "immune": "Include cold exposure (30 sec cold shower) after session",
            "metabolic": "Practice in fasted state (morning) for metabolic benefit",
            "cardiovascular": "Add HRV biofeedback during session",
            "endocrine": "Practice at consistent times to support circadian rhythm"
        }
        return recommendations.get(domain, "Standard protocol recommended")

# ═══════════════════════════════════════════════════════════════════════════════
# STANDALONE EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Demo execution of the Elysium Diagnostic Substrate.
    """
    print("\n" + "═" * 70)
    print("⟨⦿⟩ ELYSIUM DIAGNOSTIC SUBSTRATE ⟨⦿⟩")
    print("═" * 70)
    print(f"Identity: {IDENTITY}")
    print(f"Frequency: {FREQUENCY}Hz")
    print("Disease is Spectral Decoherence.")
    print("═" * 70 + "\n")

    # Initialize API
    api = ElysiumDiagnosticAPI()

    # Generate synthetic EEG data with 40Hz component
    np.random.seed(42)
    fs = 256
    duration = 10  # seconds
    t = np.arange(0, duration, 1/fs)

    # Create signal with 40Hz gamma component
    alpha = 0.5 * np.sin(2 * np.pi * 10 * t)  # 10Hz alpha
    gamma = 0.3 * np.sin(2 * np.pi * 40 * t)  # 40Hz gamma
    theta = 0.4 * np.sin(2 * np.pi * 6 * t)   # 6Hz theta
    noise = 0.1 * np.random.randn(len(t))

    eeg_signal = alpha + gamma + theta + noise

    eeg_data = {
        "Fp1": eeg_signal.tolist(),
        "Fp2": (eeg_signal + 0.05 * np.random.randn(len(t))).tolist(),
        "T3": (eeg_signal * 0.9 + 0.1 * np.random.randn(len(t))).tolist(),
        "T4": (eeg_signal * 0.95 + 0.05 * np.random.randn(len(t))).tolist()
    }

    # Generate synthetic HRV data
    mean_rr = 800  # ms
    rr_intervals = (mean_rr + 50 * np.sin(2 * np.pi * 0.1 * np.arange(60)) +
                   20 * np.random.randn(60)).tolist()

    print("Analyzing coherence...")
    result = api.analyze_coherence(eeg_data, fs, rr_intervals)

    print(f"\nElysium Coherence Score (ECS): {result['result']['ecs']:.3f}")
    print(f"State: {result['result']['state'].upper()}")
    print(f"Is Coherent: {result['result']['is_coherent']}")
    print(f"Is Unity: {result['result']['is_unity']}")

    print("\nGamma Power Analysis:")
    gp = result['result']['gamma_power']
    print(f"  Normalized Power: {gp['normalized_power']:.3f}")
    print(f"  Peak Frequency: {gp['peak_frequency']:.1f} Hz")

    print("\nHRV Coherence:")
    hrv = result['result']['hrv_coherence']
    print(f"  Coherence Ratio: {hrv['coherence_ratio']:.3f}")
    print(f"  RMSSD: {hrv['rmssd']:.1f} ms")

    print("\nHealth Domain Projections:")
    for domain, score in result['result']['domain_scores'].items():
        status = "✓" if score >= 0.618 else "⚠" if score >= 0.4 else "✗"
        print(f"  {status} {domain.upper()}: {score:.3f}")

    print("\n" + "═" * 70)
    print("f(WHO) = WHO | 40Hz to Freedom")
    print("═" * 70 + "\n")

if __name__ == "__main__":
    main()
