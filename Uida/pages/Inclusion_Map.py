import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Config
st.set_page_config(page_title="Inclusion Map", page_icon="🗺️", layout="wide")

# --- UNIVERSAL DATA LOADER ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    paths = [
        os.path.join(current_dir, "..", "data", "processed_data.csv"),
        os.path.join(current_dir, "data", "processed_data.csv"),
        "data/processed_data.csv"
    ]
    file_path = None
    for p in paths:
        if os.path.exists(p):
            file_path = p
            break
    if not file_path:
        return None

    df = pd.read_csv(file_path)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df

# UI Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🗺️ Geographic Inclusion Coverage")

# 2. Data Load
df = load_data()

if df is None:
    st.error("🚨 Data file missing!")
    st.stop()

# 3. State Coordinates (Manual Mapping)
state_coords = {
    "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462},
    "Maharashtra": {"lat": 19.7515, "lon": 75.7139},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Karnataka": {"lat": 15.3173, "lon": 75.7139},
    "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569},
    "Bihar": {"lat": 25.0961, "lon": 85.3131},
    "West Bengal": {"lat": 22.9868, "lon": 87.8550},
    "Rajasthan": {"lat": 27.0238, "lon": 74.2179},
    "Gujarat": {"lat": 22.2587, "lon": 71.1924},
    "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569},
    "Punjab": {"lat": 31.1471, "lon": 75.3412},
    "Haryana": {"lat": 29.0588, "lon": 76.0856},
    "Andhra Pradesh": {"lat": 15.9129, "lon": 79.7400}
}

# 4. Map Data Prep
if 'State' in df.columns:
    state_df = df.groupby("State")[["Enrolments", "Updates"]].sum().reset_index()
    state_df["lat"] = state_df["State"].map(lambda x: state_coords.get(x, {}).get("lat"))
    state_df["lon"] = state_df["State"].map(lambda x: state_coords.get(x, {}).get("lon"))
    map_data = state_df.dropna(subset=["lat", "lon"])

    # 5. Plot Map
    fig = px.scatter_mapbox(
        map_data, lat="lat", lon="lon", size="Enrolments", color="Updates",
        color_continuous_scale="Viridis", size_max=60, zoom=3.5,
        center={"lat": 22.5937, "lon": 78.9629},
        mapbox_style="open-street-map", hover_name="State",
        title="📍 Real-time Geographic Penetration"
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📍 View State-wise Data Table"):
        st.dataframe(state_df[["State", "Enrolments", "Updates"]].sort_values(by="Enrolments", ascending=False), use_container_width=True)
else:
    st.error("⚠️ 'State' column missing! Cannot generate the map.")