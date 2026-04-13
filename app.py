import streamlit as st


"""
app.py — The Geography of Despair
===================================
A professional Streamlit dashboard examining the geographic and economic
dimensions of the US drug overdose crisis, 1999-2022.

Run locally:
    streamlit run app.py

Deploy to Streamlit Cloud:
    1. Push this folder to GitHub
    2. Go to share.streamlit.io → New app → select your repo
    3. Main file: app.py

Dependencies (requirements.txt):
    streamlit>=1.32
    plotly>=5.18
    pandas>=2.0
    numpy>=1.24
"""


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="The Geography of Despair",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────

PALETTE = {
    "bg":       "#F7F4EF",
    "bg2":      "#EDE9E2",
    "ink":      "#1C1917",
    "ink2":     "#44403C",
    "ink3":     "#78716C",
    "rule":     "#D6D3CD",
    "coral":    "#B45309",   # amber-700 — severity / high
    "coral_lt": "#FDE68A",
    "teal":     "#0F766E",   # teal-700 — low / safe
    "teal_lt":  "#CCFBF1",
    "red":      "#9F1239",   # rose-800 — extreme
    "gold":     "#92400E",   # amber annotation
    "seq":      ["#FFF7ED","#FED7AA","#FDBA74","#FB923C","#F97316","#EA580C","#C2410C","#9A3412"],
}

# Sequential color scale for choropleth (light → dark red/amber)
SEQ_SCALE = [
    [0.0,  "#FFF7ED"],
    [0.15, "#FED7AA"],
    [0.3,  "#FDBA74"],
    [0.45, "#FB923C"],
    [0.6,  "#F97316"],
    [0.75, "#EA580C"],
    [0.88, "#C2410C"],
    [1.0,  "#7C2D12"],
]

FONT = "Georgia, 'Times New Roman', serif"
FONT_SANS = "'DM Sans', system-ui, sans-serif"

# Plotly layout defaults
BASE_LAYOUT = dict(
    font_family=FONT_SANS,
    font_color=PALETTE["ink"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=16, r=16, t=40, b=16),
    hoverlabel=dict(
        bgcolor=PALETTE["ink"],
        font_color="#F7F4EF",
        font_size=13,
        bordercolor=PALETTE["ink"],
    ),
)

# ─────────────────────────────────────────────────────────────
# CSS INJECTION
# ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

/* Root overrides */
html, body, [class*="css"] {
    font-family: 'DM Sans', system-ui, sans-serif;
    color: #1C1917;
}
.stApp { background: #F7F4EF; }

/* Remove default padding */
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* Masthead */
.masthead {
    background: #1C1917;
    color: #F7F4EF;
    padding: 36px 48px 28px;
    border-bottom: 3px solid #B45309;
}
.masthead-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #A8A29E;
    margin-bottom: 12px;
}
.masthead-title {
    font-family: Georgia, serif;
    font-size: clamp(28px, 4vw, 52px);
    font-weight: 400;
    line-height: 1.08;
    letter-spacing: -0.02em;
    margin: 0 0 12px;
}
.masthead-title em {
    font-style: italic;
    color: #FB923C;
}
.masthead-thesis {
    font-size: 14px;
    color: #A8A29E;
    max-width: 680px;
    line-height: 1.65;
    border-left: 2px solid #44403C;
    padding-left: 16px;
    margin: 0;
}

/* KPI strip */
.kpi-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: #EDE9E2;
    border-bottom: 1px solid #D6D3CD;
}
.kpi-card {
    padding: 20px 28px 18px;
    border-right: 1px solid #D6D3CD;
    position: relative;
}
.kpi-card:last-child { border-right: none; }
.kpi-bar {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-number {
    font-family: Georgia, serif;
    font-size: 38px;
    font-weight: 400;
    line-height: 1;
    letter-spacing: -0.02em;
    margin: 8px 0 6px;
}
.kpi-label {
    font-size: 12px;
    color: #78716C;
    line-height: 1.4;
}
.kpi-context {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: #A8A29E;
    margin-top: 4px;
    letter-spacing: 0.06em;
}

/* Section headers */
.section-header {
    padding: 24px 48px 0;
}
.section-rq {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #A8A29E;
    margin-bottom: 4px;
}
.section-title {
    font-family: Georgia, serif;
    font-size: 20px;
    font-weight: 400;
    color: #1C1917;
    margin-bottom: 3px;
}
.section-question {
    font-size: 12px;
    color: #78716C;
    font-style: italic;
    margin-bottom: 0;
}
.insight-bar {
    background: #FFF7ED;
    border-left: 3px solid #B45309;
    padding: 12px 16px;
    font-size: 12.5px;
    color: #44403C;
    line-height: 1.6;
    border-radius: 0 4px 4px 0;
}
.insight-bar strong { color: #9A3412; font-weight: 500; }

/* Chart containers */
.chart-panel {
    background: #F7F4EF;
    border: 1px solid #D6D3CD;
    border-radius: 8px;
    overflow: hidden;
}

/* Dividers */
.dash-divider {
    height: 1px;
    background: #D6D3CD;
    margin: 0 48px;
}

/* Footer */
.dash-footer {
    background: #1C1917;
    padding: 16px 48px;
    display: flex;
    justify-content: space-between;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: #78716C;
    margin-top: 32px;
}

/* Filter controls */
.filter-row {
    background: #EDE9E2;
    padding: 14px 48px;
    border-bottom: 1px solid #D6D3CD;
    display: flex;
    align-items: center;
    gap: 24px;
}

/* Streamlit widget overrides */
.stSelectbox > div > div { border-color: #D6D3CD !important; }
.stSlider > div > div { color: #B45309 !important; }
div[data-testid="metric-container"] { background: transparent; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────


@st.cache_data
def load_data():
    merged  = pd.read_csv("data/merged.csv")
    trend   = pd.read_csv("data/national_trend.csv")
    events  = pd.read_csv("data/events.csv")
    return merged, trend, events

df, df_trend, df_events = load_data()
state_abbrev = {
    "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA",
    "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA",
    "Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA",
    "Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD",
    "Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS",
    "Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH",
    "New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC",
    "North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA",
    "Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN",
    "Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
    "West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
}

df["state_code"] = df["state"].map(state_abbrev)
st.write("data loaded")
# ─────────────────────────────────────────────────────────────
# MASTHEAD
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="masthead">
    <div class="masthead-eyebrow">CDC WONDER · US Census ACS · 1999 – 2022 · United States</div>
    <h1 class="masthead-title">The Geography of <em>Despair</em></h1>
    <p class="masthead-thesis">
        Drug overdose is now the leading cause of accidental death in America. 
        But it is not random. The overdose crisis has a geography — and that geography 
        maps almost exactly onto economic abandonment. This is that story.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# KPI STRIP
# ─────────────────────────────────────────────────────────────

worst_state = df.loc[df["od_rate_2022"].idxmax(), "state"]
worst_rate  = df["od_rate_2022"].max()
corr_val    = df["od_rate_2022"].corr(df["poverty_rate"])
peak_year   = df_trend.loc[df_trend["rate_per_100k"].idxmax(), "year"]
peak_rate   = df_trend["rate_per_100k"].max()
growth_pct  = round((df_trend["rate_per_100k"].iloc[-1] - df_trend["rate_per_100k"].iloc[0]) /
                     df_trend["rate_per_100k"].iloc[0] * 100)

st.markdown(f"""
<div class="kpi-strip">
    <div class="kpi-card">
        <div class="kpi-bar" style="background:#7C2D12;"></div>
        <div class="kpi-number" style="color:#9A3412;">{worst_rate:.0f}</div>
        <div class="kpi-label">Deaths per 100,000 in {worst_state}</div>
        <div class="kpi-context">Highest rate in 2022 — 4× national avg</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-bar" style="background:#B45309;"></div>
        <div class="kpi-number" style="color:#92400E;">+{growth_pct}%</div>
        <div class="kpi-label">Increase in national OD rate since 1999</div>
        <div class="kpi-context">6.1 → 32.6 per 100,000</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-bar" style="background:#0F766E;"></div>
        <div class="kpi-number" style="color:#0F766E;">r = {corr_val:.2f}</div>
        <div class="kpi-label">Correlation: poverty rate vs OD mortality</div>
        <div class="kpi-context">Positive across all 50 states</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-bar" style="background:#78716C;"></div>
        <div class="kpi-number" style="color:#44403C;">{int(peak_rate)}</div>
        <div class="kpi-label">Deaths per 100k at the 2021 peak</div>
        <div class="kpi-context">5× higher than 1999 baseline</div>
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CHART 1 — CHOROPLETH MAP (Full Width)
# Research Q: Where is the crisis worst?
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="section-header">
    <div class="section-rq">RQ 1 — The map</div>
    <div class="section-title">Where is the overdose crisis worst?</div>
    <div class="section-question">"The Appalachian corridor lights up first. The pattern is not random."</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

fig_map = go.Figure(go.Choropleth(
    
    locations=df["state_code"],
    z=df["od_rate_2022"],
    locationmode="USA-states",
    colorscale=SEQ_SCALE,
    zmin=15,
    zmax=85,
    colorbar=dict(
        title=dict(text="Deaths per 100k", font=dict(size=11, family=FONT_SANS, color=PALETTE["ink3"])),
        thickness=12,
        len=0.65,
        x=1.01,
        tickfont=dict(size=10, family=FONT_SANS),
        tickvals=[20, 35, 50, 65, 80],
        ticktext=["20", "35", "50", "65", "80+"],
    ),
    hovertemplate=(
        "<b>%{location}</b><br>"
        "OD rate: %{z:.1f} per 100,000<extra></extra>"
    ),
    marker_line_color="#F7F4EF",
    marker_line_width=0.8,
))

fig_map.update_layout(
    **BASE_LAYOUT,
    geo=dict(
        scope="usa",
        bgcolor="rgba(0,0,0,0)",
        lakecolor="#F7F4EF",
        landcolor="#EDE9E2",
        showlakes=True,
        showcoastlines=False,
        showframe=False,
    ),
    height=420,
    
)

st.plotly_chart(fig_map, use_container_width=True)

col_insight1, _ = st.columns([2, 1])
with col_insight1:
    st.markdown("""
    <div class="insight-bar">
        <strong>West Virginia (80.9), Kentucky (52.8), Tennessee (50.7), Ohio (48.1)</strong> form a 
        contiguous high-mortality corridor. These are former manufacturing and mining states that 
        experienced the sharpest job losses from 1990–2010. The geography of overdose is, 
        in large part, the geography of deindustrialization.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
st.markdown("<div class='dash-divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CHART 2 — TIMELINE (Full Width)
# Research Q: When did this happen and what triggered each wave?
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="section-header">
    <div class="section-rq">RQ 2 — The timeline</div>
    <div class="section-title">Three waves in twenty-four years</div>
    <div class="section-question">"The crisis arrived in three distinct surges, each driven by a different substance."</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

fig_trend = go.Figure()

# Shaded wave regions
wave_regions = [
    dict(x0=1999, x1=2010, label="Wave 1\nPrescription opioids", color="#FED7AA"),
    dict(x0=2010, x1=2016, label="Wave 2\nHeroin",              color="#FDBA74"),
    dict(x0=2016, x1=2022, label="Wave 3\nSynthetic opioids",   color="#FB923C"),
]
for w in wave_regions:
    fig_trend.add_vrect(
        x0=w["x0"], x1=w["x1"],
        fillcolor=w["color"], opacity=0.18,
        layer="below", line_width=0,
    )
    fig_trend.add_annotation(
        x=(w["x0"] + w["x1"]) / 2,
        y=33.5,
        text=w["label"].replace("\n", "<br>"),
        showarrow=False,
        font=dict(size=9.5, family=FONT_SANS, color=PALETTE["gold"]),
        align="center",
    )

# Main trend line
fig_trend.add_trace(go.Scatter(
    x=df_trend["year"],
    y=df_trend["rate_per_100k"],
    mode="lines+markers",
    line=dict(color=PALETTE["coral"], width=2.5),
    marker=dict(size=5, color=PALETTE["coral"],
                line=dict(color=PALETTE["bg"], width=1.5)),
    hovertemplate="<b>%{x}</b><br>%{y:.1f} deaths per 100,000<extra></extra>",
    name="National OD rate",
))

# Event annotations
event_data = {
    1999: "OxyContin\nlaunched",
    2010: "Rx crackdown\nbegins",
    2016: "Fentanyl\nsurges",
    2020: "COVID-19",
}
for yr, label in event_data.items():
    rate = df_trend.loc[df_trend["year"] == yr, "rate_per_100k"].values
    if len(rate):
        fig_trend.add_annotation(
            x=yr, y=rate[0],
            text=label.replace("\n", "<br>"),
            showarrow=True,
            arrowhead=0,
            arrowwidth=1,
            arrowcolor=PALETTE["ink3"],
            ax=0, ay=-38,
            font=dict(size=9, family=FONT_SANS, color=PALETTE["ink2"]),
            align="center",
            bgcolor=PALETTE["bg"],
            bordercolor=PALETTE["rule"],
            borderwidth=0.5,
            borderpad=4,
        )

fig_trend.update_layout(
    **BASE_LAYOUT,
    height=340,
    showlegend=False,
    xaxis=dict(
        title=None,
        gridcolor=PALETTE["rule"],
        gridwidth=0.5,
        tickfont=dict(size=11),
        dtick=3,
    ),
    yaxis=dict(
    title=dict(
        text="Deaths per 100,000 (age-adjusted)",
        font=dict(size=11, color=PALETTE["ink3"])
    ),
        gridcolor=PALETTE["rule"],
        gridwidth=0.5,
        tickfont=dict(size=11),
        range=[0, 37],
    ),
    
)

with st.container():
    # Year range filter
    col_sl, col_sp = st.columns([3, 1])
    with col_sl:
        yr_range = st.slider(
            "Filter year range",
            min_value=1999, max_value=2022,
            value=(1999, 2022),
            label_visibility="collapsed",
        )

    mask = (df_trend["year"] >= yr_range[0]) & (df_trend["year"] <= yr_range[1])
    fig_trend_filtered = go.Figure(fig_trend)
    fig_trend_filtered.data[0].x = df_trend.loc[mask, "year"]
    fig_trend_filtered.data[0].y = df_trend.loc[mask, "rate_per_100k"]
    fig_trend_filtered.update_xaxes(range=[yr_range[0] - 0.5, yr_range[1] + 0.5])
    st.plotly_chart(fig_trend_filtered, use_container_width=True)

col_insight2, _ = st.columns([2, 1])
with col_insight2:
    st.markdown("""
    <div class="insight-bar">
        The rate was essentially flat 1999–2006, then began climbing. 
        <strong>The 2016 inflection point is the fentanyl moment</strong> — the year 
        synthetic opioids overtook heroin. From 27.1 in 2020 to 32.6 in 2022, 
        the pandemic added acceleration. The crisis has no plateau.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
st.markdown("<div class='dash-divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# CHARTS 3 + 4 — TWO COLUMN LAYOUT
# ─────────────────────────────────────────────────────────────


# ── CHART 3: SCATTER — Poverty vs OD rate ──



# Filter controls
highlight_opt = st.selectbox(
    "Highlight region",
    ["All states", "Appalachia", "South", "Midwest", "West", "Northeast"],
    label_visibility="collapsed",
)

REGIONS = {
    "Appalachia":  ["West Virginia","Kentucky","Tennessee","Ohio","Pennsylvania","Virginia","North Carolina","Georgia","Alabama","Mississippi"],
    "South":       ["Texas","Florida","Louisiana","Arkansas","Mississippi","Alabama","Georgia","South Carolina","North Carolina","Tennessee"],
    "Midwest":     ["Illinois","Indiana","Iowa","Kansas","Michigan","Minnesota","Missouri","Nebraska","North Dakota","Ohio","South Dakota","Wisconsin"],
    "West":        ["Alaska","Arizona","California","Colorado","Hawaii","Idaho","Montana","Nevada","New Mexico","Oregon","Utah","Washington","Wyoming"],
    "Northeast":   ["Connecticut","Delaware","Maine","Maryland","Massachusetts","New Hampshire","New Jersey","New York","Pennsylvania","Rhode Island","Vermont"],
}

df_plot = df.copy()
if highlight_opt != "All states":
    region_states = REGIONS.get(highlight_opt, [])
    df_plot["highlight"] = df_plot["state"].isin(region_states)
else:
    df_plot["highlight"] = True

# Trendline
z = np.polyfit(df_plot["poverty_rate"], df_plot["od_rate_2022"], 1)
p = np.poly1d(z)
x_line = np.linspace(df_plot["poverty_rate"].min(), df_plot["poverty_rate"].max(), 100)

fig_scatter = go.Figure()

# Trendline
fig_scatter.add_trace(go.Scatter(
    x=x_line, y=p(x_line),
    mode="lines",
    line=dict(color=PALETTE["coral"], width=1.5, dash="dash"),
    showlegend=False,
    hoverinfo="skip",
))

# Non-highlighted points
if highlight_opt != "All states":
    df_grey = df_plot[~df_plot["highlight"]]
    fig_scatter.add_trace(go.Scatter(
        x=df_grey["poverty_rate"],
        y=df_grey["od_rate_2022"],
        mode="markers",
        marker=dict(size=8, color=PALETTE["rule"], opacity=0.5),
        text=df_grey["state"],
        hovertemplate="<b>%{text}</b><br>Poverty: %{x:.1f}%<br>OD rate: %{y:.1f}<extra></extra>",
        showlegend=False,
    ))

# Highlighted / main points
df_hi = df_plot[df_plot["highlight"]]

fig_scatter.add_trace(go.Scatter(
x=df_hi["poverty_rate"],
y=df_hi["od_rate_2022"],
mode="markers",
marker=dict(
    size=9,
    color=PALETTE["coral"],
    opacity=0.75,
    line=dict(color="#F7F4EF", width=1)
),
text=df_hi["state"],
hovertemplate="<b>%{text}</b><br>Poverty: %{x:.1f}%<br>OD rate: %{y:.1f} per 100k<extra></extra>",
showlegend=False,
))

# WV label
wv = df[df["state"] == "West Virginia"].iloc[0]
fig_scatter.add_annotation(
    x=wv["poverty_rate"], y=wv["od_rate_2022"],
    text="<b>West Virginia</b><br>80.9 per 100k",
    showarrow=True, arrowhead=0, arrowcolor=PALETTE["red"],
    ax=40, ay=-30,
    font=dict(size=9.5, color=PALETTE["red"]),
    bgcolor=PALETTE["bg"], bordercolor=PALETTE["red"],
    borderwidth=0.8, borderpad=4,
)

fig_scatter.update_layout(
    **BASE_LAYOUT,
    height=380,
    xaxis=dict(
title=dict(
    text="Poverty rate (%)",
    font=dict(size=11, color=PALETTE["ink3"])
),
        gridcolor=PALETTE["rule"], gridwidth=0.5,
        ticksuffix="%",
    ),
    yaxis=dict(
title=dict(
    text="OD deaths per 100,000",
    font=dict(size=11, color=PALETTE["ink3"])
),
        gridcolor=PALETTE["rule"], gridwidth=0.5,
    ),
)
poverty_med = df["poverty_rate"].median()
od_med = df["od_rate_2022"].median()

fig_scatter.add_vline(
    x=poverty_med,
    line_dash="dot",
    line_color=PALETTE["rule"]
)

fig_scatter.add_hline(
    y=od_med,
    line_dash="dot",
    line_color=PALETTE["rule"]
)
fig_scatter.add_annotation(
    x=0.02, y=0.98,
    xref="paper", yref="paper",
    text="High poverty<br>High overdose",
    showarrow=False,
    align="left",
    font=dict(size=10, color=PALETTE["ink3"])
)

fig_scatter.add_annotation(
    x=0.98, y=0.02,
    xref="paper", yref="paper",
    text="Low poverty<br>Low overdose",
    showarrow=False,
    align="right",
    font=dict(size=10, color=PALETTE["ink3"])
)




# ── CHART 4: OUTLIERS — CLEAN + BALANCED ──


# Regression
z = np.polyfit(df["poverty_rate"], df["od_rate_2022"], 1)
p = np.poly1d(z)

df["expected_od"] = p(df["poverty_rate"])
df["residual"] = df["od_rate_2022"] - df["expected_od"]

# Top outliers (sorted for horizontal bar readability)
df_outliers = df.sort_values("residual", ascending=False).head(10).sort_values("residual")

# 🎯 CLEAN COLOR STRATEGY (only highlight the worst)
colors = [PALETTE["ink3"]] * len(df_outliers)
colors[-1] = PALETTE["red"]  # highlight top outlier only

fig_outliers = go.Figure(go.Bar(
    y=df_outliers["state_code"],  # 👈 use abbreviations (cleaner)
    x=df_outliers["residual"],
    orientation="h",
    marker=dict(
        color=colors,
        line=dict(color="rgba(0,0,0,0)", width=0)
    ),
    hovertemplate="<b>%{y}</b><br>Excess OD rate: %{x:.1f}<extra></extra>",
))

fig_outliers.update_layout(
    **BASE_LAYOUT,
    height=280,
    xaxis=dict(
        title=dict(
            text="Excess deaths vs expected",
            font=dict(size=11, color=PALETTE["ink3"])
        ),
        gridcolor=PALETTE["rule"],
        zeroline=True,
        zerolinecolor=PALETTE["ink3"],
        zerolinewidth=1
    ),
    yaxis=dict(
        tickfont=dict(size=11),
        gridcolor="rgba(0,0,0,0)"
    ),
    bargap=0.35,
)
# 🔥 Add zero baseline (very important for interpretation)
fig_outliers.add_vline(
    x=0,
    line_dash="dash",
    line_color=PALETTE["ink3"],
    line_width=1,
)
fig_outliers.add_vrect(
    x0=0,
    x1=df_outliers["residual"].max() * 1.05,
    fillcolor=PALETTE["coral_lt"],
    opacity=0.15,
    layer="below",
    line_width=0
)
# 🔥 Annotate top outlier
top_state = df_outliers.iloc[-1]

fig_outliers.add_annotation(
    x=top_state["residual"],
    y=top_state["state_code"],
    text=f"<b>{top_state['state_code']}</b>",
    showarrow=True,
    arrowhead=0,
    ax=30,
    ay=0,
    font=dict(size=10, color=PALETTE["red"]),
    bgcolor=PALETTE["bg"],
    bordercolor=PALETTE["red"],
    borderwidth=0.8,
)
fig_outliers.add_annotation(
    x=0,
    y=1.08,
    yref="paper",
    text="← lower than expected   higher than expected →",
    showarrow=False,
    font=dict(size=10, color=PALETTE["ink3"]),
)




# ── CHARTS 3 + 4 — FINAL LAYOUT ──
col_left, col_right = st.columns(2, gap="large")

# LEFT COLUMN — SCATTER
with col_left:

    st.markdown("""
    <div class="section-rq">RQ 3 — The correlation</div>
    <div class="section-title">Poverty predicts overdose</div>
    <div class="section-question" style="margin-bottom:12px;">
    "Is economic distress driving the pattern?"
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(fig_scatter, use_container_width=True, key="scatter")

    st.markdown(f"""
    <div class="insight-bar">
        Across all 50 states, poverty rate and overdose mortality show a 
        <strong>positive correlation (r = {corr_val:.2f})</strong>. 
        Economic distress is not the only factor — but it is the most consistent predictor.
    </div>
    """, unsafe_allow_html=True)


# RIGHT COLUMN — OUTLIERS
with col_right:

    st.markdown("""
    <div class="section-rq">RQ 4 — The deviation</div>
    <div class="section-title">Where reality diverges from expectation</div>
    <div class="section-question" style="margin-bottom:12px;">
    "Which states perform worse than economic conditions alone would predict?"
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(fig_outliers, use_container_width=True, key="outliers")

    st.markdown("""
    <div class="insight-bar">
        States like <strong>WV and KY</strong> significantly exceed predicted levels. 
        This suggests that structural factors beyond poverty — including opioid supply 
        and healthcare access — are driving excess mortality.
    </div>
    """, unsafe_allow_html=True)


# ── CHART 5: DISTRIBUTION — How concentrated is the crisis ──
# ── CHART 5: DISTRIBUTION — A crisis driven by extremes ──
# ── CHART 5: DISTRIBUTION — STABLE VERSION ──
st.markdown("""
<div class="section-rq">RQ 5 — The distribution</div>
<div class="section-title">A crisis driven by extremes</div>
<div class="section-question" style="margin-bottom:12px;">
"Is the burden evenly spread, or concentrated among a few states?"
</div>
""", unsafe_allow_html=True)

fig_dist = go.Figure()

# Histogram ONLY (safe)
fig_dist.add_trace(go.Histogram(
    x=df["od_rate_2022"],
    nbinsx=15,
    marker=dict(
        color=PALETTE["coral"],
        opacity=0.5,
    ),
    hovertemplate="Rate: %{x:.1f}<br>States: %{y}<extra></extra>",
))

# National average line
nat_avg = df["od_rate_2022"].mean()

fig_dist.add_vline(
    x=nat_avg,
    line_dash="dash",
    line_color=PALETTE["ink"],
    line_width=2,
)

# IMPORTANT: remove yref="paper" (causes frontend issues)
fig_dist.add_annotation(
    x=nat_avg,
    y=df["od_rate_2022"].count() * 0.6,
    text=f"Avg: {nat_avg:.0f}",
    showarrow=False,
    font=dict(size=10, color=PALETTE["ink"]),
)

fig_dist.update_layout(
    **BASE_LAYOUT,
    height=300,
    xaxis=dict(
        title=dict(
            text="Overdose deaths per 100,000",
            font=dict(size=11, color=PALETTE["ink3"])
        ),
        gridcolor=PALETTE["rule"],
    ),
    yaxis=dict(
        title="Number of states",
        gridcolor=PALETTE["rule"],
    ),
)

st.plotly_chart(fig_dist, use_container_width=True, key="distribution")

st.markdown("""
<div class="insight-bar">
The distribution is heavily right-skewed. Most states cluster in a mid-range, 
while a small number of extreme outliers disproportionately drive the crisis.
</div>
""", unsafe_allow_html=True)
# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="dash-footer">
    <span>
        Sources: CDC WONDER Multiple Cause of Death Database (ICD-10 X40–X44, X60–X64, X85, Y10–Y14) · 
        US Census Bureau American Community Survey 5-Year Estimates (2022) · 
        CDC NCHS Data Brief No. 491 (2023)
    </span>
    <span>The Geography of Despair · All rates age-adjusted per 100,000</span>
</div>
""", unsafe_allow_html=True)
