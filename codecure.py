from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from typing import Optional
import math

app = FastAPI(
    title="Codecure API",
    description="Counterfactual Health Understanding Engine",
    version="1.0.0"
)

# ==============================
# CORS — required for React frontend
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Input Models with validation
# ==============================
class LifestyleInputs(BaseModel):
    sleep: float = Field(..., ge=0, le=24, description="Sleep hours (0–24)")
    screen: float = Field(..., ge=0, le=24, description="Screen hours (0–24)")
    steps: int = Field(..., ge=0, le=50000, description="Steps per day")
    meals: float = Field(..., ge=0, le=1, description="Meal regularity (0–1)")
    stress_input: float = Field(..., ge=1, le=10, description="Stress level (1–10)")
    water: float = Field(..., ge=0, le=10, description="Water intake in litres")

    @model_validator(mode="after")
    def sleep_plus_screen_check(self):
        if self.sleep + self.screen > 24:
            raise ValueError("Sleep + screen time cannot exceed 24 hours")
        return self

class SimulationRequest(BaseModel):
    actual: LifestyleInputs
    counterfactual: Optional[LifestyleInputs] = None  # user-defined what-if

# ==============================
# Core calculation (clamped outputs)
# ==============================
def calculate_metrics(inputs: LifestyleInputs) -> dict:
    raw_stress = (
        0.4 * max(8 - inputs.sleep, 0) +   # sleep deficit
        0.3 * inputs.screen +
        0.2 * inputs.stress_input -
        0.0002 * inputs.steps -
        0.5 * inputs.meals -
        0.3 * inputs.water
    )
    stress = round(max(0.0, min(raw_stress, 10.0)), 2)  # clamp 0–10

    raw_fatigue = (
        0.5 * stress +
        0.4 * max(8 - inputs.sleep, 0) -
        0.3 * (inputs.steps / 10000) -
        0.2 * inputs.water
    )
    fatigue = round(max(0.0, min(raw_fatigue, 10.0)), 2)  # clamp 0–10

    # Derived wellness score (0–100, higher is better)
    wellness = round(100 - (stress * 5 + fatigue * 5), 1)
    wellness = max(0.0, min(wellness, 100.0))

    return {"stress": stress, "fatigue": fatigue, "wellness": wellness}

# ==============================
# Impact ranking (all scores positive)
# ==============================
def rank_interventions(actual: LifestyleInputs) -> list:
    scores = {
        "sleep":        abs(0.4 * max(8 - actual.sleep, 0)),
        "screen":       abs(0.3 * actual.screen),
        "steps":        abs(0.0002 * max(10000 - actual.steps, 0)),
        "meals":        abs(0.5 * (1 - actual.meals)),
        "stress_input": abs(0.2 * actual.stress_input),
        "water":        abs(0.3 * max(3 - actual.water, 0)),
    }
    labels = {
        "sleep":        "Increase sleep to 8h",
        "screen":       "Reduce screen time",
        "steps":        "Walk more — target 10,000 steps",
        "meals":        "Eat at regular intervals",
        "stress_input": "Practice stress management",
        "water":        "Drink more water (target 3L)",
    }
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {
            "factor": k,
            "impact_score": round(v, 3),
            "advice": labels[k]
        }
        for k, v in ranked if v > 0
    ]

# ==============================
# Auto-generate counterfactual
# if user didn't provide one
# ==============================
def auto_counterfactual(actual: LifestyleInputs) -> LifestyleInputs:
    return LifestyleInputs(
        sleep=min(actual.sleep + 2, 9),      # ↑ increase more
        screen=max(actual.screen - 2, 0),    # ↓ stronger change
        steps=min(actual.steps + 4000, 15000),
        meals=min(actual.meals + 0.3, 1),
        stress_input=max(actual.stress_input - 2, 1),
        water=min(actual.water + 1.5, 10),
    )

# ==============================
# Routes
# ==============================
@app.get("/")
def home():
    return {"message": "Codecure API running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/simulate")
def simulate(request: SimulationRequest):
    actual = request.actual
    counterfactual = request.counterfactual or auto_counterfactual(actual)

    actual_metrics = calculate_metrics(actual)
    cf_metrics = calculate_metrics(counterfactual)

    stress_delta   = round(actual_metrics["stress"]   - cf_metrics["stress"],   2)
    fatigue_delta  = round(actual_metrics["fatigue"]  - cf_metrics["fatigue"],  2)
    wellness_delta = round(cf_metrics["wellness"]     - actual_metrics["wellness"], 2)

    print("ACTUAL:", actual.model_dump())
    print("COUNTERFACTUAL:", counterfactual.model_dump())

    interventions = rank_interventions(actual)
    top_factor = interventions[0] if interventions else {}

    return {
        "actual": {
            "inputs": actual.model_dump(),
            "metrics": actual_metrics,
        },
        "counterfactual": {
            "inputs": counterfactual.model_dump(),
            "metrics": cf_metrics,
        },
        "impact": {
            "stress_reduction":   stress_delta,
            "fatigue_reduction":  fatigue_delta,
            "wellness_gain":      wellness_delta,
            "regret_score":       round(wellness_delta * 1.2, 1),  # novel metric
        },
        "interventions": interventions,
        "insight": {
            "top_factor": top_factor.get("factor", ""),
            "advice": top_factor.get("advice", ""),
            "narrative": (
                f"If you had made these lifestyle changes, your stress would have "
                f"dropped by {stress_delta} points and your wellness score would have "
                f"improved by {wellness_delta} points. "
                f"Your biggest lever right now is: {top_factor.get('advice', '')}."
            )
        }
    }
from timeline  import router as timeline_router
from narrative import router as narrative_router

app.include_router(timeline_router)
app.include_router(narrative_router)
