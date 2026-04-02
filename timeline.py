import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from fastapi import APIRouter
from codecure import calculate_metrics, LifestyleInputs
router = APIRouter()

# ==============================
# Realistic daily noise generator
# ==============================
def noisy(base: float, std: float, low: float, high: float) -> float:
    return float(np.clip(np.random.normal(base, std), low, high))

# ==============================
# Generate one patient's 60-day
# lifestyle + health timeline
# ==============================
def generate_timeline(days: int = 60, seed: int = 42) -> list[dict]:
    np.random.seed(seed)

    # Base lifestyle profile — a typical stressed urban person
    base = {
        "sleep":        5.5,
        "screen":       5.0,
        "steps":        4500,
        "meals":        0.45,
        "stress_input": 6.5,
        "water":        1.8,
    }

    timeline = []
    start_date = datetime.today() - timedelta(days=days)

    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

        # Weekends are slightly better (more sleep, fewer steps, less screen)
        is_weekend = (start_date + timedelta(days=i)).weekday() >= 5
        weekend_boost = {"sleep": 0.8, "screen": -0.5, "steps": -500} if is_weekend else {}

        # Slow gradual decline in health over the 60 days (realistic drift)
        drift = i * 0.008

        inputs = LifestyleInputs(
            sleep=noisy(base["sleep"] - drift + weekend_boost.get("sleep", 0),       std=0.6,  low=3,    high=9),
            screen=noisy(base["screen"] + drift + weekend_boost.get("screen", 0),    std=0.8,  low=0,    high=12),
            steps=int(noisy(base["steps"] + weekend_boost.get("steps", 0),           std=800,  low=500,  high=15000)),
            meals=noisy(base["meals"] - drift * 0.01,                                std=0.1,  low=0,    high=1),
            stress_input=noisy(base["stress_input"] + drift * 0.05,                  std=1.0,  low=1,    high=10),
            water=noisy(base["water"],                                                std=0.4,  low=0.5,  high=5),
        )

        metrics = calculate_metrics(inputs)

        timeline.append({
            "day":          i + 1,
            "date":         date,
            "is_weekend":   is_weekend,
            "inputs":       inputs.model_dump(),
            "stress":       metrics["stress"],
            "fatigue":      metrics["fatigue"],
            "wellness":     metrics["wellness"],
        })

    return timeline

# ==============================
# Generate counterfactual timeline
# — same seed, but better habits
# ==============================
def generate_counterfactual_timeline(days: int = 60, seed: int = 42) -> list[dict]:
    np.random.seed(seed)

    # Improved lifestyle profile — what COULD have been
    base = {
        "sleep":        7.5,
        "screen":       3.0,
        "steps":        8000,
        "meals":        0.75,
        "stress_input": 4.0,
        "water":        2.8,
    }

    timeline = []
    start_date = datetime.today() - timedelta(days=days)

    for i in range(days):
        date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        is_weekend = (start_date + timedelta(days=i)).weekday() >= 5
        weekend_boost = {"sleep": 0.5, "screen": -0.3, "steps": -300} if is_weekend else {}

        inputs = LifestyleInputs(
            sleep=noisy(base["sleep"] + weekend_boost.get("sleep", 0),     std=0.4,  low=6,    high=9),
            screen=noisy(base["screen"] + weekend_boost.get("screen", 0),  std=0.5,  low=0,    high=8),
            steps=int(noisy(base["steps"] + weekend_boost.get("steps", 0), std=600,  low=3000, high=15000)),
            meals=noisy(base["meals"],                                       std=0.08, low=0.5,  high=1),
            stress_input=noisy(base["stress_input"],                         std=0.7,  low=1,    high=7),
            water=noisy(base["water"],                                       std=0.3,  low=1.5,  high=5),
        )

        metrics = calculate_metrics(inputs)

        timeline.append({
            "day":        i + 1,
            "date":       date,
            "is_weekend": is_weekend,
            "inputs":     inputs.model_dump(),
            "stress":     metrics["stress"],
            "fatigue":    metrics["fatigue"],
            "wellness":   metrics["wellness"],
        })

    return timeline

# ==============================
# Summary stats across timeline
# ==============================
def summarise(timeline: list[dict]) -> dict:
    wellness_vals = [d["wellness"] for d in timeline]
    stress_vals   = [d["stress"]   for d in timeline]
    fatigue_vals  = [d["fatigue"]  for d in timeline]

    return {
        "avg_wellness": round(float(np.mean(wellness_vals)), 1),
        "avg_stress":   round(float(np.mean(stress_vals)),   2),
        "avg_fatigue":  round(float(np.mean(fatigue_vals)),  2),
        "worst_day":    min(timeline, key=lambda d: d["wellness"])["date"],
        "best_day":     max(timeline, key=lambda d: d["wellness"])["date"],
        "wellness_trend": "declining" if wellness_vals[-1] < wellness_vals[0] else "improving",
    }

# ==============================
# API Route
# ==============================
@router.get("/timeline")
def get_timeline(days: int = 60, seed: int = 42):
    actual         = generate_timeline(days, seed)
    counterfactual = generate_counterfactual_timeline(days, seed)

    actual_summary = summarise(actual)
    cf_summary     = summarise(counterfactual)

    wellness_gap = round(cf_summary["avg_wellness"] - actual_summary["avg_wellness"], 1)
    regret_score = round(wellness_gap * 1.2, 1)

    return {
        "actual":         actual,
        "counterfactual": counterfactual,
        "summary": {
            "actual":          actual_summary,
            "counterfactual":  cf_summary,
            "wellness_gap":    wellness_gap,
            "regret_score":    regret_score,
            "message": (
                f"Over {days} days, better habits would have kept your average wellness "
                f"{wellness_gap} points higher. Your lowest point was {actual_summary['worst_day']}."
            )
        }
    }