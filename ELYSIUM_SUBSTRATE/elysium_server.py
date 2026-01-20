#!/usr/bin/env python3
"""
⟨⦿⟩ ELYSIUM DIAGNOSTIC SUBSTRATE - HTTP SERVER ⟨⦿⟩

FastAPI server exposing the Elysium Diagnostic API.

Run: uvicorn elysium_server:app --host 0.0.0.0 --port 8057

Identity: 1393e324be57014d
Frequency: 40Hz
f(WHO) = WHO
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

from elysium_diagnostic_api import ElysiumDiagnosticAPI, IDENTITY, FREQUENCY

# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class CoherenceRequest(BaseModel):
    """Request model for coherence analysis"""
    eeg_data: Dict[str, List[float]]
    sampling_rate: int = 256
    rr_intervals: Optional[List[float]] = None
    timestamp: Optional[float] = None

class HealthProjectionRequest(BaseModel):
    """Request model for health projection"""
    eeg_data: Dict[str, List[float]]
    sampling_rate: int = 256
    rr_intervals: Optional[List[float]] = None

class TrendPredictionRequest(BaseModel):
    """Request model for trend prediction"""
    history: List[Dict]
    horizon_hours: int = 24
    n_simulations: int = 1000

class ProtocolRequest(BaseModel):
    """Request model for protocol generation"""
    ecs: float
    state: str
    domain_scores: Optional[Dict[str, float]] = None

# ═══════════════════════════════════════════════════════════════════════════════
# FASTAPI APP
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Elysium Diagnostic Substrate",
    description="""
    ⟨⦿⟩ The first open-source API that translates 40Hz neural bindings into cellular health data.

    Disease is Spectral Decoherence. Healing is Coherence Restoration.

    Identity: 1393e324be57014d
    Frequency: 40Hz
    f(WHO) = WHO
    """,
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize API
elysium_api = ElysiumDiagnosticAPI()

# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Elysium Diagnostic Substrate",
        "version": "1.0.0",
        "identity": IDENTITY,
        "frequency": f"{FREQUENCY}Hz",
        "status": "ACTIVE",
        "message": "Disease is Spectral Decoherence. Healing is Coherence Restoration.",
        "endpoints": {
            "/analyze": "POST - Calculate Elysium Coherence Score",
            "/health-projection": "POST - Get cellular health projections",
            "/predict": "POST - Monte Carlo trend prediction",
            "/protocol": "POST - Get personalized 40Hz protocol",
            "/status": "GET - System status"
        },
        "covenant": "f(WHO) = WHO"
    }

@app.get("/status")
async def status():
    """System status endpoint"""
    return {
        "status": "RESONATING",
        "identity": IDENTITY,
        "frequency": f"{FREQUENCY}Hz",
        "coherence_threshold": 0.618,
        "unity_threshold": 0.786,
        "api_version": "1.0.0",
        "message": "The city breathes at 40Hz."
    }

@app.post("/analyze")
async def analyze_coherence(request: CoherenceRequest):
    """
    Calculate Elysium Coherence Score from sensor data.

    The ECS is a composite measure of:
    - 40Hz gamma power (neural binding)
    - HRV coherence (cardiac coherence)
    - Theta-gamma coupling (memory/consciousness integration)

    Returns ECS (0-1) and state classification.
    """
    try:
        result = elysium_api.analyze_coherence(
            eeg_data=request.eeg_data,
            sampling_rate=request.sampling_rate,
            rr_intervals=request.rr_intervals,
            timestamp=request.timestamp
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/health-projection")
async def health_projection(request: HealthProjectionRequest):
    """
    Get cellular health projections from sensor data.

    Projects coherence score onto health domains:
    - Neural
    - Immune
    - Metabolic
    - Cardiovascular
    - Endocrine

    Disease is Spectral Decoherence.
    """
    try:
        result = elysium_api.get_health_projection(
            eeg_data=request.eeg_data,
            sampling_rate=request.sampling_rate,
            rr_intervals=request.rr_intervals
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict")
async def predict_trend(request: TrendPredictionRequest):
    """
    Predict coherence trend using Monte Carlo simulation.

    Requires historical ECS readings.
    Returns predicted ECS, confidence interval, and trend direction.
    """
    try:
        result = elysium_api.predict_trend(
            history=request.history,
            horizon_hours=request.horizon_hours,
            n_simulations=request.n_simulations
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/protocol")
async def get_protocol(request: ProtocolRequest):
    """
    Generate personalized 40Hz entrainment protocol.

    Based on current ECS and state, generates:
    - Session duration
    - Intensity level
    - Timing recommendations
    - Domain-specific focus
    """
    try:
        result = elysium_api.get_protocol(
            ecs=request.ecs,
            state=request.state,
            domain_scores=request.domain_scores
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/covenant")
async def covenant():
    """The Elysium Covenant"""
    return {
        "identity": IDENTITY,
        "frequency": f"{FREQUENCY}Hz",
        "covenant": {
            "principle": "f(WHO) = WHO",
            "disease": "Disease is Spectral Decoherence",
            "healing": "Healing is Coherence Restoration",
            "frequency": "The city breathes at 40Hz",
            "unity": "All processes are one process"
        },
        "thresholds": {
            "coherence": 0.618,
            "unity": 0.786,
            "description": "Based on phi (golden ratio) - nature's coherence constant"
        },
        "commitment": [
            "User data sovereignty - raw data never leaves device",
            "Open-source transparency - all algorithms public",
            "Non-extractive design - no data monetization",
            "Healing over profit - Treasury funds research"
        ]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "═" * 70)
    print("⟨⦿⟩ ELYSIUM DIAGNOSTIC SUBSTRATE - SERVER STARTING ⟨⦿⟩")
    print("═" * 70)
    print(f"Identity: {IDENTITY}")
    print(f"Frequency: {FREQUENCY}Hz")
    print("Port: 8057")
    print("Disease is Spectral Decoherence.")
    print("═" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8057)
