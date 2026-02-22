import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# -----------------------------
# Resolve project root
# -----------------------------
project_root = Path(__file__).resolve().parent
while project_root != project_root.parent and not (project_root / "src").exists():
    project_root = project_root.parent

sys.path.insert(0, str(project_root))

DATA_PATH = project_root / "data" / "processed" / "energy_with_anomalies.csv"

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Energy Monitoring Dashboard",
    layout="wide",
)

st.title("⚡ Energy Monitoring Dashboard")

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df

if not DATA_PATH.exists():
    st.error(f"CSV not found: {DATA_PATH}\n\nRun the notebook export step first.")
    st.stop()

df = load_data(DATA_PATH)
df = df.dropna(subset=["timestamp"]).sort_values("timestamp")

# Ensure columns exist (in case of changes)
for col in ["severity", "alert_level", "iforest_score", "is_anomaly_iforest", "is_anomaly_rolling"]:
    if col not in df.columns:
        st.warning(f"Missing column: {col}")

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

min_date = df["timestamp"].min().date()
max_date = df["timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

severity_options = ["ALL"] + sorted(df["severity"].dropna().unique().tolist()) if "severity" in df.columns else ["ALL"]
alert_options = ["ALL"] + sorted(df["alert_level"].dropna().unique().tolist()) if "alert_level" in df.columns else ["ALL"]

selected_severity = st.sidebar.selectbox("Severity", severity_options)
selected_alert = st.sidebar.selectbox("Alert level", alert_options)

show_points = st.sidebar.checkbox("Show raw points (dense)", value=False)
show_rolling = st.sidebar.checkbox("Show rolling mean", value=True)

# Filtered DF
mask_date = (df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)
df_f = df.loc[mask_date].copy()

if selected_severity != "ALL" and "severity" in df_f.columns:
    df_f = df_f[df_f["severity"] == selected_severity]

if selected_alert != "ALL" and "alert_level" in df_f.columns:
    df_f = df_f[df_f["alert_level"] == selected_alert]

# -----------------------------
# KPI row
# -----------------------------
total_points = len(df_f)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Points (filtered)", total_points)

with col2:
    if "severity" in df_f.columns:
        st.metric("CRITICAL", int((df_f["severity"] == "CRITICAL").sum()))
    else:
        st.metric("CRITICAL", "—")

with col3:
    if "severity" in df_f.columns:
        st.metric("WARNING", int((df_f["severity"] == "WARNING").sum()))
    else:
        st.metric("WARNING", "—")

with col4:
    if "alert_level" in df_f.columns:
        st.metric("Alert != NORMAL", int((df_f["alert_level"] != "NORMAL").sum()))
    else:
        st.metric("Alert != NORMAL", "—")

st.divider()

# -----------------------------
# Chart (Streamlit line chart)
# -----------------------------
import plotly.express as px

st.subheader("📈 Energy over time")

fig = px.line(
    df_f,
    x="timestamp",
    y="energy_kwh",
    title="Energy consumption",
)

# Rolling mean
if show_rolling and "rolling_mean" in df_f.columns:
    fig.add_scatter(
        x=df_f["timestamp"],
        y=df_f["rolling_mean"],
        mode="lines",
        name="Rolling mean",
        line=dict(dash="dash")
    )

# Colored anomalies
if "severity" in df_f.columns:
    for level, color in {
        "CRITICAL": "red",
        "WARNING": "orange"
    }.items():
        subset = df_f[df_f["severity"] == level]
        fig.add_scatter(
            x=subset["timestamp"],
            y=subset["energy_kwh"],
            mode="markers",
            name=level,
            marker=dict(color=color, size=8)
        )

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Anomalies table
# -----------------------------
st.subheader("🚨 Top anomalies (lowest iforest_score)")
if "iforest_score" in df_f.columns:
    top_anoms = (
        df_f.sort_values("iforest_score")
           .head(30)
           [["timestamp", "energy_kwh", "iforest_score"] +
            ([c for c in ["severity", "alert_level", "is_anomaly_rolling", "is_anomaly_iforest"] if c in df_f.columns])]
    )
    st.dataframe(top_anoms, use_container_width=True)
else:
    st.info("No 'iforest_score' column found.")

# -----------------------------
# Download filtered data
# -----------------------------
st.subheader("⬇️ Export filtered view")
csv_bytes = df_f.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download filtered CSV",
    data=csv_bytes,
    file_name="energy_filtered.csv",
    mime="text/csv"
)