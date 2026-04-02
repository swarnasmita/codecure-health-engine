import os
import json
import httpx
from fastapi import APIRouter
from pydantic import BaseModel
from models import LifestyleInputs
from health import calculate_metrics

router = APIRouter()

OPENAI_API_KEY = "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"

class NarrativeRequest(BaseModel):
    actual: LifestyleInputs
    counterfactual: LifestyleInputs

def build_prompt(actual, actual_metrics, cf, cf_metrics, impact, interventions) -> str:
    return f"""
You are a compassionate but honest health advisor inside an AI system called Codecure.

A patient's ACTUAL lifestyle over the past 60 days:
- Sleep: {actual.sleep}h/night
- Screen time: {actual.screen}h/day
- Steps: {actual.steps}/day
- Meal regularity: {actual.meals * 100:.0f}%
- Stress level: {actual.stress_input}/10
- Water intake: {actual.water}L/day

Actual health metrics:
- Stress score: {actual_metrics['stress']}/10
- Fatigue score: {actual_metrics['fatigue']}/10
- Wellness score: {actual_metrics['wellness']}/100

Counterfactual lifestyle (what could have been):
- Sleep: {cf.sleep}h/night
- Screen time: {cf.screen}h/day
- Steps: {cf.steps}/day
- Meal regularity: {cf.meals * 100:.0f}%
- Stress level: {cf.stress_input}/10
- Water intake: {cf.water}L/day

Counterfactual health metrics:
- Stress score: {cf_metrics['stress']}/10
- Fatigue score: {cf_metrics['fatigue']}/10
- Wellness score: {cf_metrics['wellness']}/100

Impact of missed choices:
- Stress reduction missed: {impact['stress_reduction']} points
- Fatigue reduction missed: {impact['fatigue_reduction']} points
- Wellness gain missed: {impact['wellness_gain']} points
- Regret score: {impact['regret_score']}

Top intervention: {interventions[0]['factor']} — {interventions[0]['advice']}

Respond ONLY in this exact JSON format, no extra text, no markdown:
{{
  "headline": "One punchy sentence summarising what was lost (max 15 words)",
  "what_happened": "2-3 sentences explaining what the actual lifestyle did to their body in plain language",
  "alternate_reality": "2-3 sentences painting a vivid picture of how their body would have felt in the counterfactual scenario",
  "biggest_mistake": "1 sentence naming the single most impactful poor habit and its consequence",
  "action_now": "1 concrete specific action they can start today",
  "regret_label": "A 3-4 word emotional label for the regret score"
}}
"""

async def call_openai(prompt: str) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=body
        )
        response.raise_for_status()
        data = response.json()

    return json.loads(data["choices"][0]["message"]["content"])

def compute_impact(actual_metrics: dict, cf_metrics: dict) -> dict:
    return {
        "stress_reduction":  round(actual_metrics["stress"]  - cf_metrics["stress"],  2),
        "fatigue_reduction": round(actual_metrics["fatigue"] - cf_metrics["fatigue"], 2),
        "wellness_gain":     round(cf_metrics["wellness"]    - actual_metrics["wellness"], 2),
        "regret_score":      round((cf_metrics["wellness"]   - actual_metrics["wellness"]) * 1.2, 1),
    }

@router.post("/narrative")
async def generate_narrative(request: NarrativeRequest):
    actual_metrics = calculate_metrics(request.actual)
    cf_metrics     = calculate_metrics(request.counterfactual)
    impact         = compute_impact(actual_metrics, cf_metrics)

    from codecure import rank_interventions
    interventions = rank_interventions(request.actual)

    prompt = build_prompt(
        request.actual, actual_metrics,
        request.counterfactual, cf_metrics,
        impact, interventions
    )

    try:
        narrative = await call_openai(prompt)
    except Exception as e:
        # In narrative.py, update the fallback block
        narrative = {
            "headline": f"Better habits could have gained you {impact['wellness_gain']} wellness points.",
            "what_happened": (
                f"Your {request.actual.sleep}h of sleep and {request.actual.stress_input}/10 "
                f"stress pushed your body into a sustained high-stress state over 60 days."
            ),
            "alternate_reality": (
                f"With {request.counterfactual.sleep}h of sleep and reduced screen time, "
                f"your wellness score would have been {cf_metrics['wellness']}/100 instead "
                f"of {actual_metrics['wellness']}/100."
            ),
            "biggest_mistake": "Poor sleep was your highest-impact habit — fix this first.",
            "action_now": "Set a fixed sleep time tonight and keep screens off 30 minutes before bed.",
            "regret_label": "Significant health loss" if impact["regret_score"] > 10 else "Moderate missed opportunity"
        }
        

    return {
        "narrative": narrative,
        "metrics": {
            "actual":         actual_metrics,
            "counterfactual": cf_metrics,
            "impact":         impact,
        }
    }