import streamlit as st
import requests
import plotly.graph_objects as go
import json

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
API_BASE = "http://localhost:8000"

st.set_page_config(
    page_title="Codecure",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# CSS — Warm Charcoal + Amber + Crimson
# Medical-editorial aesthetic
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

:root {
    --ink:       #111008;
    --paper:     #161410;
    --card:      #1e1b16;
    --border:    #2e2820;
    --amber:     #e8a012;
    --amber-dim: #8a5e08;
    --crimson:   #c93535;
    --sage:      #6b8c6e;
    --text:      #d4c9b0;
    --muted:     #6e6355;
    --highlight: #f5e6c0;
}

html, body, [class*="css"] {
    background-color: var(--ink);
    color: var(--text);
    font-family: 'Crimson Pro', Georgia, serif;
}

.stApp {
    background: var(--ink);
    background-image:
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(232,160,18,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(201,53,53,0.04) 0%, transparent 60%);
}

/* ── HEADER ── */
.cc-header {
    padding: 3rem 0 2rem;
    display: flex;
    align-items: flex-end;
    gap: 2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
}
.cc-logo-block { flex: 1; }
.cc-logo {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5.5rem;
    line-height: 0.9;
    letter-spacing: 0.06em;
    color: var(--highlight);
    text-shadow: 2px 2px 0 var(--amber-dim), 0 0 60px rgba(232,160,18,0.15);
    margin: 0;
}
.cc-logo span { color: var(--amber); }
.cc-tagline {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 300;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.6rem;
}
.cc-version {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: var(--amber-dim);
    border: 1px solid var(--amber-dim);
    padding: 0.2rem 0.6rem;
    border-radius: 2px;
    margin-bottom: 0.5rem;
    align-self: flex-start;
    margin-top: auto;
}

/* ── SECTION HEADINGS ── */
.cc-section {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    color: var(--amber);
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.cc-section::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border) 0%, transparent 100%);
}

/* ── SLIDER LABEL OVERRIDES ── */
label[data-testid="stWidgetLabel"] p {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* ── METRIC CARDS ── */
.cc-metric {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.6rem 1.4rem 1.3rem;
    position: relative;
    overflow: hidden;
}
.cc-metric::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
}
.cc-metric.amber::after   { background: linear-gradient(90deg, var(--amber), transparent); }
.cc-metric.crimson::after { background: linear-gradient(90deg, var(--crimson), transparent); }
.cc-metric.sage::after    { background: linear-gradient(90deg, var(--sage), transparent); }
.cc-metric-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.8rem;
    line-height: 1;
    letter-spacing: 0.04em;
    margin: 0;
}
.cc-metric.amber  .cc-metric-val { color: var(--amber); }
.cc-metric.crimson .cc-metric-val { color: var(--crimson); }
.cc-metric.sage   .cc-metric-val { color: var(--sage); }
.cc-metric-lbl {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.5rem;
}
.cc-metric-sub {
    font-family: 'Crimson Pro', serif;
    font-size: 0.85rem;
    color: var(--muted);
    font-style: italic;
    margin-top: 0.2rem;
}

/* ── NARRATIVE ── */
.cc-narrative {
    background: var(--card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--amber);
    border-radius: 4px;
    padding: 2rem 2.2rem;
    font-family: 'Crimson Pro', Georgia, serif;
    font-size: 1.25rem;
    font-style: italic;
    line-height: 1.9;
    color: var(--text);
    position: relative;
}
.cc-narrative::before {
    content: '"';
    font-family: 'Bebas Neue', sans-serif;
    font-size: 5rem;
    color: var(--amber-dim);
    position: absolute;
    top: -0.5rem;
    left: 1.2rem;
    line-height: 1;
    opacity: 0.5;
}

/* ── INTERVENTION CARDS ── */
.cc-interv {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.7rem;
    display: grid;
    grid-template-columns: 2.5rem 2rem 1fr auto;
    align-items: center;
    gap: 1rem;
}
.cc-interv-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    line-height: 1;
}
.cc-interv-icon { font-size: 1.4rem; }
.cc-interv-text {
    font-family: 'Crimson Pro', serif;
    font-size: 1.1rem;
    color: var(--highlight);
}
.cc-interv-bar-wrap {
    height: 3px;
    background: var(--border);
    border-radius: 2px;
    margin-top: 0.4rem;
}
.cc-interv-bar { height: 3px; border-radius: 2px; }
.cc-interv-score {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    white-space: nowrap;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    background: transparent !important;
    border-radius: 0 !important;
    padding: 0.7rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--amber) !important;
    border-bottom: 2px solid var(--amber) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── BUTTON ── */
div[data-testid="stButton"] > button {
    background: transparent !important;
    color: var(--amber) !important;
    border: 1px solid var(--amber) !important;
    border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.25em !important;
    text-transform: uppercase !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
    margin-top: 0.5rem !important;
}
div[data-testid="stButton"] > button:hover {
    background: var(--amber) !important;
    color: var(--ink) !important;
    box-shadow: 0 0 30px rgba(232,160,18,0.25) !important;
}

/* ── EMPTY STATE ── */
.cc-empty {
    text-align: center;
    padding: 5rem 2rem;
}
.cc-empty-glyph {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 8rem;
    color: var(--border);
    line-height: 1;
}
.cc-empty-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 1rem;
    line-height: 2;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stDecoration"] { display: none; }
.block-container { padding-top: 1rem !important; }

div[data-testid="stSlider"] p {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--amber);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="cc-header">
    <div class="cc-logo-block">
        <div class="cc-logo">CODE<span>CURE</span></div>
        <div class="cc-tagline">Counterfactual Health Understanding Engine &nbsp;·&nbsp; What if you'd chosen differently?</div>
    </div>
    <div class="cc-version">v 1.0.0</div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────
def call_simulate(actual, counterfactual=None):
    payload = {"actual": actual}
    if counterfactual:
        payload["counterfactual"] = counterfactual
    try:
        r = requests.post(f"{API_BASE}/simulate", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(30,27,22,0.9)",
    font=dict(family="IBM Plex Mono, monospace", color="#6e6355", size=11),
    margin=dict(l=48, r=24, t=36, b=48),
    xaxis=dict(gridcolor="#2e2820", zerolinecolor="#2e2820", color="#6e6355"),
    yaxis=dict(gridcolor="#2e2820", zerolinecolor="#2e2820", color="#6e6355"),
)


# ─────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────
left, right = st.columns([1, 1.9], gap="large")

# ══════════════════════════════
# LEFT — INPUT LAB
# ══════════════════════════════
with left:
    st.markdown('<div class="cc-section">Input Lab</div>', unsafe_allow_html=True)

    tab_a, tab_cf = st.tabs(["YOUR ACTUAL WEEK", "WHAT IF SCENARIO"])

    with tab_a:
        sleep  = st.slider("Sleep hours",        0.0, 24.0, 6.0,  0.5,  key="sl")
        screen = st.slider("Screen hours",       0.0, 18.0, 6.0,  0.5,  key="sc")
        steps  = st.slider("Daily steps",        0,  20000, 5000, 500,   key="st")
        meals  = st.slider("Meal regularity",    0.0,  1.0, 0.5,  0.05, key="ml",
                           help="0 = skipping meals · 1 = perfectly regular")
        stress = st.slider("Stress level",       1.0, 10.0, 7.0,  0.5,  key="sx")
        water  = st.slider("Water intake  (L)",  0.0, 10.0, 1.5,  0.25, key="wt")

        if sleep + screen > 24:
            st.warning("Sleep + screen time exceeds 24 hours.")

    with tab_cf:
        auto = st.toggle("Auto-generate optimal counterfactual", value=True)
        if not auto:
            cf_sleep  = st.slider("Sleep hours",      0.0, 24.0, min(sleep+1.5, 9.0),   0.5,  key="csl")
            cf_screen = st.slider("Screen hours",     0.0, 18.0, max(screen-1.0, 0.0),  0.5,  key="csc")
            cf_steps  = st.slider("Daily steps",      0,  20000, min(steps+2000,15000),  500,  key="cst")
            cf_meals  = st.slider("Meal regularity",  0.0,  1.0, min(meals+0.2, 1.0),   0.05, key="cml")
            cf_stress = st.slider("Stress level",     1.0, 10.0, max(stress-1.0, 1.0),  0.5,  key="csx")
            cf_water  = st.slider("Water intake (L)", 0.0, 10.0, min(water+1.0, 10.0),  0.25, key="cwt")
        else:
            st.info("The engine will derive the optimal counterfactual automatically from your inputs.")

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    run = st.button("RUN SIMULATION →", key="run")


# ══════════════════════════════
# RIGHT — RESULTS
# ══════════════════════════════
with right:
    st.markdown('<div class="cc-section">Simulation Results</div>', unsafe_allow_html=True)

    if not run and "result" not in st.session_state:
        st.markdown("""
        <div class="cc-empty">
            <div class="cc-empty-glyph">⬡</div>
            <div class="cc-empty-text">
                Set your lifestyle inputs<br>
                and run the simulation<br>
                to reveal your health divergence
            </div>
        </div>
        """, unsafe_allow_html=True)

    if run:
        actual_p = dict(sleep=sleep, screen=screen, steps=steps,
                        meals=meals, stress_input=stress, water=water)
        cf_p = None
        if not auto:
            cf_p = dict(sleep=cf_sleep, screen=cf_screen, steps=cf_steps,
                        meals=cf_meals, stress_input=cf_stress, water=cf_water)

        with st.spinner("Reconstructing alternate reality…"):
            res = call_simulate(actual_p, cf_p)

        if res is None:
            st.error("Cannot reach API at localhost:8000 — start with:  uvicorn main:app --reload")
        else:
            st.session_state["result"] = res

    if "result" in st.session_state:
        R   = st.session_state["result"]
        im  = R["impact"]
        am  = R["actual"]["metrics"]
        cm  = R["counterfactual"]["metrics"]
        ins = R["insight"]
        ivs = R["interventions"]
        max_score = max(x["impact_score"] for x in ivs) if ivs else 1

        # ── Four metric cards ──
        c1, c2, c3, c4 = st.columns(4)
        cards = [
            (c1, "crimson", f"▼ {im['stress_reduction']}",  "Stress\nReduction",  "points less stress"),
            (c2, "crimson", f"▼ {im['fatigue_reduction']}", "Fatigue\nReduction", "points less fatigue"),
            (c3, "sage",    f"▲ {im['wellness_gain']}",     "Wellness\nGain",     "point improvement"),
            (c4, "amber",   f"{im['regret_score']}",        "Regret\nScore",      "cost of inaction"),
        ]
        for col, cls, val, lbl, sub in cards:
            with col:
                st.markdown(f"""
                <div class="cc-metric {cls}">
                    <div class="cc-metric-val">{val}</div>
                    <div class="cc-metric-lbl">{lbl}</div>
                    <div class="cc-metric-sub">{sub}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)

        # ── Three tabs ──
        t1, t2, t3 = st.tabs(["DIVERGENCE CHARTS", "INTERVENTION RANKING", "CASE NARRATIVE"])

        # ── DIVERGENCE ──
        with t1:
            col_a, col_b = st.columns(2)

            with col_a:
                cats = ["Stress", "Fatigue", "Wellness"]
                av   = [am["stress"], am["fatigue"], am["wellness"]/10]
                cv   = [cm["stress"], cm["fatigue"], cm["wellness"]/10]

                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=av+[av[0]], theta=cats+[cats[0]], fill='toself', name='Actual',
                    line=dict(color='#c93535', width=2.5),
                    fillcolor='rgba(201,53,53,0.12)',
                ))
                fig.add_trace(go.Scatterpolar(
                    r=cv+[cv[0]], theta=cats+[cats[0]], fill='toself', name='Counterfactual',
                    line=dict(color='#e8a012', width=2.5),
                    fillcolor='rgba(232,160,18,0.10)',
                ))
                fig.update_layout(
                    polar=dict(
                        bgcolor='rgba(30,27,22,0.9)',
                        radialaxis=dict(visible=True, range=[0,10],
                                        gridcolor='#2e2820', color='#6e6355',
                                        tickfont=dict(family='IBM Plex Mono', size=10)),
                        angularaxis=dict(gridcolor='#2e2820', color='#d4c9b0',
                                         tickfont=dict(family='Crimson Pro', size=13)),
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    legend=dict(font=dict(family='IBM Plex Mono', color='#d4c9b0', size=10),
                                bgcolor='rgba(0,0,0,0)'),
                    margin=dict(l=30, r=30, t=40, b=30),
                    height=310,
                    title=dict(text="HEALTH PROFILE",
                               font=dict(family='IBM Plex Mono', color='#6e6355', size=9), x=0.5),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_b:
                metrics_lbl = ["Stress", "Fatigue", "Wellness (÷10)"]
                actual_v    = [am["stress"], am["fatigue"], am["wellness"]/10]
                cf_v        = [cm["stress"], cm["fatigue"], cm["wellness"]/10]

                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    name='Actual', y=metrics_lbl, x=actual_v,
                    orientation='h', marker_color='#c93535', marker_opacity=0.8,
                    marker_line_width=0,
                ))
                fig2.add_trace(go.Bar(
                    name='Counterfactual', y=metrics_lbl, x=cf_v,
                    orientation='h', marker_color='#e8a012', marker_opacity=0.8,
                    marker_line_width=0,
                ))
                fig2.update_layout(
                    barmode='group', height=310,
                    title=dict(text="METRIC COMPARISON",
                               font=dict(family='IBM Plex Mono', color='#6e6355', size=9), x=0.5),
                    legend=dict(font=dict(family='IBM Plex Mono', color='#d4c9b0', size=10),
                                bgcolor='rgba(0,0,0,0)'),
                    **PLOTLY_BASE,
                )
                st.plotly_chart(fig2, use_container_width=True)

            # Wellness gauge
            fig3 = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=cm["wellness"],
                delta=dict(reference=am["wellness"],
                           increasing=dict(color="#6b8c6e"),
                           decreasing=dict(color="#c93535"),
                           font=dict(family='IBM Plex Mono', size=16)),
                number=dict(font=dict(family='Bebas Neue', size=52, color='#e8a012')),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor='#6e6355',
                              tickfont=dict(family='IBM Plex Mono', size=10)),
                    bar=dict(color="#e8a012", thickness=0.25),
                    bgcolor='rgba(30,27,22,0.9)',
                    borderwidth=1, bordercolor='#2e2820',
                    steps=[
                        dict(range=[0,40],   color='rgba(201,53,53,0.15)'),
                        dict(range=[40,70],  color='rgba(232,160,18,0.10)'),
                        dict(range=[70,100], color='rgba(107,140,110,0.12)'),
                    ],
                    threshold=dict(line=dict(color="#c93535", width=2), value=am["wellness"]),
                ),
                title=dict(text="COUNTERFACTUAL WELLNESS SCORE",
                           font=dict(family='IBM Plex Mono', color='#6e6355', size=9)),
            ))
            fig3.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='IBM Plex Mono', color='#6e6355'),
                height=240,
                margin=dict(l=40, r=40, t=40, b=10),
            )
            st.plotly_chart(fig3, use_container_width=True)

        # ── INTERVENTIONS ──
        with t2:
            icons = {"sleep":"😴","screen":"📵","steps":"🚶","meals":"🥗",
                     "stress_input":"🧘","water":"💧"}
            rank_colors = ["#e8a012","#c93535","#6b8c6e","#6e6355","#6e6355","#6e6355"]

            for i, item in enumerate(ivs):
                icon  = icons.get(item["factor"], "·")
                score = item["impact_score"]
                pct   = int((score / max_score) * 100)
                color = rank_colors[i] if i < len(rank_colors) else "#6e6355"
                st.markdown(f"""
                <div class="cc-interv">
                    <span class="cc-interv-num" style="color:{color}">0{i+1}</span>
                    <span class="cc-interv-icon">{icon}</span>
                    <div>
                        <div class="cc-interv-text">{item['advice']}</div>
                        <div class="cc-interv-bar-wrap">
                            <div class="cc-interv-bar"
                                 style="width:{pct}%;background:{color};opacity:0.7"></div>
                        </div>
                    </div>
                    <span class="cc-interv-score">impact<br>{score:.3f}</span>
                </div>
                """, unsafe_allow_html=True)

        # ── NARRATIVE ──
        with t3:
            st.markdown(f"""
            <div class="cc-narrative">
                {ins['narrative']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-family:'IBM Plex Mono',monospace; font-size:0.72rem;
                        color:var(--muted); letter-spacing:0.15em; line-height:2;">
                TOP LEVER &nbsp;·&nbsp;
                <span style="color:var(--amber)">{ins['top_factor'].upper()}</span>
                &nbsp;—&nbsp; {ins['advice']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            with st.expander("RAW SIMULATION PAYLOAD"):
                st.json(R)


# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("""
<div style="border-top:1px solid #2e2820; margin-top:3rem; padding:1.5rem 0 2rem;
            text-align:center; font-family:'IBM Plex Mono',monospace;
            font-size:0.6rem; letter-spacing:0.3em; color:#2e2820; text-transform:uppercase;">
    Codecure &nbsp;·&nbsp; Counterfactual Health Understanding Engine &nbsp;·&nbsp; v1.0.0
</div>
""", unsafe_allow_html=True)