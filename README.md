# codecure-health-engine
# 🧠 CODECURE: The Road Not Taken  
### An AI Engine for Alternate Health Outcomes

---

## 🚨 Problem

Healthcare today is like a GPS that only tells you where you are —  
never where you went wrong, and never:

> *“What if you had taken a different route?”*

We are surrounded by health dashboards:
- Step counts  
- Heart rate  
- Sleep scores  

But none of them answer the only question that truly matters:

> ❓ *What would my body look like today if I had made better choices?*

We are drowning in **health data**, but starving for **health understanding**.

---

## 💡 Solution: Codecure

**Codecure is a counterfactual health intelligence engine.**

It doesn’t just:
- Track your health ❌  
- Predict your future ❌  

👉 It reconstructs your past and simulates your **alternate reality**.

> “Here’s the version of you that slept 8 hours.  
> And here’s exactly what you lost by not doing it.”

That’s not health tracking.  
That’s **health truth**.

---

## 🧠 Core Idea

Codecure answers:

> 🛣️ *“What path did your health take… and what path could it have taken?”*

It builds:
- A **causal model of lifestyle → health**
- A **counterfactual simulation engine**
- A **decision intelligence system**

---

## 👤 Impact

### 🧍 For Patients
- Moves from generic advice → **personalized evidence**
- Shows *your* behavior → *your* consequences  
- Example:
  > “Your late-night screen time increased your stress by 18%”

👉 People change when they see **their own cause-effect**

---

### 🩺 For Doctors
- Turns consultation into **forensic analysis**
- Provides:
  - Ranked behavioral causes  
  - What-if simulations in real time  

👉 Not guessing — **evidence-based lifestyle modeling**

---

### 🌍 For Healthcare Systems
- Targets **preventable diseases (80% of costs)**
- Enables:
  - Early intervention  
  - Behavior correction  
  - Reduced treatment burden  

👉 Shift from **treatment → prevention**
---

## 📁 Project Structure

---

## 🔧 Backend Components

### 🧠 1. `codecure.py` (Main Engine)
- Input validation
- Health score calculation
- Counterfactual simulation
- Impact analysis
- Intervention ranking

👉 Core endpoint:POST /simulate

---

### 🧾 2. `narrative.py` 
- Uses LLM to generate:
  - Health story
  - Regret explanation
  - Actionable advice

👉 Converts numbers → **human understanding**

---

### 📈 3. `timeline.py` 
- Simulates **60-day health journey**
- Generates:
  - Actual vs counterfactual timeline  
  - Trends & decline patterns  

👉 Shows **how your health diverged over time**

---

## 🎨 Frontend

### `codecure_app.py`
- Built using **Streamlit**
- Interactive sliders:
  - Sleep  
  - Screen time  
  - Steps  
  - Meals  
  - Stress  
  - Water  

- Displays:
  - 📊 Metrics (stress, fatigue, wellness)  
  - 📉 Impact  
  - 📈 Charts  
  - 🧠 Narrative  
  - 🏆 Ranked interventions  

---

## 🚀 How to Run

### 🔹 1. Install dependencies
pip install -r requirements.txt

---

### 🔹 2. Run Backend
uvicorn codecure:app

---

### 🔹 3. Run Frontend
streamlit run codecure_app.py

---

### 🔹 4. Open in browser
http://localhost:8501

---

## 🧪 Example Input

```json
{
  "sleep": 5,
  "screen": 6,
  "steps": 4000,
  "meals": 0.4,
  "stress_input": 7,
  "water": 1.5
}
📊 Example Output
Stress reduced by: 1.9
Fatigue reduced by: 1.8
Wellness increased by: 17 points
Most impactful factor: Screen Time
```
Key Innovations

- Counterfactual health simulation
- Personalized causal reasoning
- Intervention ranking
- Narrative intelligence (AI explanation)
- Timeline reconstruction
- Regret scoring (novel metric)

Author:
Swarnasmita Roy

