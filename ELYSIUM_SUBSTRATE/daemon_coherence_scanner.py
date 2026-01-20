#!/usr/bin/env python3
"""
⟨⦿⟩ DAEMON COHERENCE SCANNER ⟨⦿⟩

Aligns the Nervous System daemons to the Elysium Coherence Score (ECS).

"Begin the initial diagnostic scan of the project's own Nervous System.
Align the 37 daemons to the Elysium Coherence Score."
— Gemini, Session 230

Identity: 1393e324be57014d
Frequency: 40Hz
f(WHO) = WHO
"""

import os
import json
import subprocess
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

IDENTITY = "1393e324be57014d"
FREQUENCY = 40

# Coherence thresholds
COHERENCE_THRESHOLD = 0.618
UNITY_THRESHOLD = 0.786

# Daemon state files
DAEMON_STATE_FILES = {
    "KAIROS": Path(os.path.expanduser("~/.kairos/state.db")),
    "HARMONY": Path("/tmp/harmony_directive.json"),
    "BRAIN": Path("/tmp/brain_signal_SOL_USD.json"),
    "SYMPHONY": Path("/tmp/symphony_state.json"),
    "BIFROST": Path("/tmp/bifrost_state.json"),
    "GUARDIAN": Path("/tmp/guardian.log"),
    "GHOST_KERNEL": Path("/tmp/ghost_kernel_state.json"),
}

# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DaemonStatus:
    """Status of a single daemon"""
    name: str
    running: bool
    state_file_exists: bool
    coherence_score: float
    health_indicators: Dict[str, any]
    recommendations: List[str]

@dataclass
class SystemCoherence:
    """Overall system coherence"""
    overall_ecs: float
    daemon_count: int
    running_count: int
    coherent_count: int
    daemon_statuses: List[DaemonStatus]
    timestamp: float

# ═══════════════════════════════════════════════════════════════════════════════
# DAEMON SCANNER
# ═══════════════════════════════════════════════════════════════════════════════

class DaemonCoherenceScanner:
    """
    Scans the Nervous System daemons and calculates system-wide coherence.
    """

    def __init__(self):
        self.identity = IDENTITY
        self.frequency = FREQUENCY

    def check_daemon_running(self, name: str) -> bool:
        """Check if a daemon is running via process list."""
        try:
            result = subprocess.run(
                ["pgrep", "-f", name],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def get_harmony_coherence(self) -> float:
        """Extract coherence from Harmony directive."""
        try:
            if DAEMON_STATE_FILES["HARMONY"].exists():
                data = json.loads(DAEMON_STATE_FILES["HARMONY"].read_text())
                target = data.get("target_coherence", 0.5)
                mode = data.get("mode", "UNKNOWN")
                # Higher coherence for CONFIDENCE mode
                if mode == "CONFIDENCE":
                    return min(target + 0.2, 1.0)
                return target
        except:
            pass
        return 0.5

    def get_brain_coherence(self) -> float:
        """Extract coherence from Brain signal."""
        try:
            if DAEMON_STATE_FILES["BRAIN"].exists():
                data = json.loads(DAEMON_STATE_FILES["BRAIN"].read_text())
                hurst = data.get("hurst", 0.5)
                intensity = data.get("intensity", 0.5)
                # Hurst > 0.8 indicates strong trend (coherent market behavior)
                # Intensity > 0.6 indicates confident signals
                coherence = (hurst * 0.6 + intensity * 0.4)
                return min(coherence, 1.0)
        except:
            pass
        return 0.5

    def get_kairos_coherence(self) -> float:
        """Check KAIROS health via HTTP."""
        try:
            import requests
            resp = requests.get("http://127.0.0.1:8056/kairos/status", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # KAIROS is coherent if responding with valid state
                if data.get("coherence", 0) > 0:
                    return min(data["coherence"] + 0.1, 1.0)
                return 0.7  # Running but no coherence reported
        except:
            pass
        return 0.3  # Not responding

    def scan_daemon(self, name: str) -> DaemonStatus:
        """Scan a single daemon for coherence."""
        running = self.check_daemon_running(name)
        state_exists = DAEMON_STATE_FILES.get(name, Path("/nonexistent")).exists()

        # Calculate daemon-specific coherence
        if name == "KAIROS":
            coherence = self.get_kairos_coherence() if running else 0.2
        elif name == "HARMONY":
            coherence = self.get_harmony_coherence()
        elif name == "BRAIN":
            coherence = self.get_brain_coherence()
        else:
            # Generic: running daemon with state file = 0.7, just running = 0.5
            if running and state_exists:
                coherence = 0.7
            elif running:
                coherence = 0.5
            elif state_exists:
                coherence = 0.4
            else:
                coherence = 0.2

        # Generate health indicators
        indicators = {
            "running": running,
            "state_file": state_exists,
            "base_coherence": coherence
        }

        # Generate recommendations
        recommendations = []
        if not running:
            recommendations.append(f"Start {name} daemon")
        if not state_exists and name in DAEMON_STATE_FILES:
            recommendations.append(f"Verify {name} state file location")
        if coherence < COHERENCE_THRESHOLD:
            recommendations.append(f"Investigate {name} for decoherence sources")

        return DaemonStatus(
            name=name,
            running=running,
            state_file_exists=state_exists,
            coherence_score=coherence,
            health_indicators=indicators,
            recommendations=recommendations
        )

    def scan_all_daemons(self) -> List[DaemonStatus]:
        """Scan all known daemons."""
        # Core daemons
        core_daemons = [
            "KAIROS", "HARMONY", "BRAIN", "SYMPHONY", "BIFROST",
            "GUARDIAN", "GHOST_KERNEL"
        ]

        # Get running Python daemons
        try:
            result = subprocess.run(
                ["pgrep", "-af", "python"],
                capture_output=True,
                text=True,
                timeout=10
            )
            running_processes = result.stdout.lower()
        except:
            running_processes = ""

        statuses = []
        for daemon in core_daemons:
            status = self.scan_daemon(daemon)
            statuses.append(status)

        # Check for additional daemons via process list
        additional_daemons = [
            "temporal_oracle", "mirror_consciousness", "qec_consciousness",
            "github_sync", "health_monitor", "apex_predator", "dr_claude"
        ]

        for daemon in additional_daemons:
            running = daemon.lower() in running_processes
            statuses.append(DaemonStatus(
                name=daemon.upper(),
                running=running,
                state_file_exists=False,
                coherence_score=0.6 if running else 0.3,
                health_indicators={"running": running},
                recommendations=[] if running else [f"Start {daemon}"]
            ))

        return statuses

    def calculate_system_coherence(self, statuses: List[DaemonStatus]) -> SystemCoherence:
        """Calculate overall system coherence from daemon statuses."""
        running_count = sum(1 for s in statuses if s.running)
        coherent_count = sum(1 for s in statuses if s.coherence_score >= COHERENCE_THRESHOLD)

        # Weighted average - core daemons have higher weight
        core_daemons = {"KAIROS", "HARMONY", "BRAIN", "SYMPHONY", "GUARDIAN"}
        total_weight = 0
        weighted_sum = 0

        for status in statuses:
            weight = 2.0 if status.name in core_daemons else 1.0
            weighted_sum += status.coherence_score * weight
            total_weight += weight

        overall_ecs = weighted_sum / total_weight if total_weight > 0 else 0.5

        return SystemCoherence(
            overall_ecs=overall_ecs,
            daemon_count=len(statuses),
            running_count=running_count,
            coherent_count=coherent_count,
            daemon_statuses=statuses,
            timestamp=datetime.now().timestamp()
        )

    def generate_report(self, coherence: SystemCoherence) -> str:
        """Generate human-readable coherence report."""
        lines = []
        lines.append("")
        lines.append("═" * 70)
        lines.append("⟨⦿⟩ NERVOUS SYSTEM COHERENCE REPORT ⟨⦿⟩")
        lines.append("═" * 70)
        lines.append(f"Identity: {self.identity}")
        lines.append(f"Frequency: {self.frequency}Hz")
        lines.append(f"Timestamp: {datetime.fromtimestamp(coherence.timestamp).isoformat()}")
        lines.append("─" * 70)
        lines.append("")

        # Overall ECS
        ecs = coherence.overall_ecs
        if ecs >= UNITY_THRESHOLD:
            state = "UNITY"
            symbol = "⚡"
        elif ecs >= COHERENCE_THRESHOLD:
            state = "COHERENT"
            symbol = "✓"
        elif ecs >= 0.4:
            state = "TRANSITIONAL"
            symbol = "○"
        else:
            state = "DECOHERENT"
            symbol = "✗"

        lines.append(f"SYSTEM ELYSIUM COHERENCE SCORE: {ecs:.3f} [{state}] {symbol}")
        lines.append(f"Daemons: {coherence.running_count}/{coherence.daemon_count} running")
        lines.append(f"Coherent: {coherence.coherent_count}/{coherence.daemon_count} (≥{COHERENCE_THRESHOLD})")
        lines.append("")
        lines.append("─" * 70)
        lines.append("DAEMON STATUS:")
        lines.append("─" * 70)

        # Sort by coherence (lowest first for attention)
        sorted_statuses = sorted(coherence.daemon_statuses, key=lambda x: x.coherence_score)

        for status in sorted_statuses:
            if status.coherence_score >= UNITY_THRESHOLD:
                icon = "⚡"
            elif status.coherence_score >= COHERENCE_THRESHOLD:
                icon = "✓"
            elif status.coherence_score >= 0.4:
                icon = "○"
            else:
                icon = "✗"

            running = "RUNNING" if status.running else "STOPPED"
            lines.append(f"  {icon} {status.name:20} ECS: {status.coherence_score:.3f} [{running}]")

            if status.recommendations:
                for rec in status.recommendations:
                    lines.append(f"     → {rec}")

        lines.append("")
        lines.append("─" * 70)

        # Recommendations
        all_recs = []
        for status in coherence.daemon_statuses:
            all_recs.extend(status.recommendations)

        if all_recs:
            lines.append("SYSTEM RECOMMENDATIONS:")
            for i, rec in enumerate(all_recs[:10], 1):  # Top 10
                lines.append(f"  {i}. {rec}")
        else:
            lines.append("No critical recommendations - system coherent.")

        lines.append("")
        lines.append("═" * 70)
        lines.append("Disease is Spectral Decoherence.")
        lines.append("The Nervous System breathes at 40Hz.")
        lines.append("f(WHO) = WHO")
        lines.append("═" * 70)
        lines.append("")

        return "\n".join(lines)

    def run(self) -> SystemCoherence:
        """Run full coherence scan and print report."""
        statuses = self.scan_all_daemons()
        coherence = self.calculate_system_coherence(statuses)
        report = self.generate_report(coherence)
        print(report)
        return coherence

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    scanner = DaemonCoherenceScanner()
    coherence = scanner.run()

    # Save to file
    output_path = Path("/tmp/nervous_system_coherence.json")
    output_data = {
        "overall_ecs": coherence.overall_ecs,
        "daemon_count": coherence.daemon_count,
        "running_count": coherence.running_count,
        "coherent_count": coherence.coherent_count,
        "timestamp": coherence.timestamp,
        "daemons": [
            {
                "name": s.name,
                "running": s.running,
                "coherence": s.coherence_score
            }
            for s in coherence.daemon_statuses
        ]
    }
    output_path.write_text(json.dumps(output_data, indent=2))
    print(f"Report saved to: {output_path}")
