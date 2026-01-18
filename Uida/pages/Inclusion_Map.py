import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Config
st.set_page_config(page_title="Inclusion Map", page_icon="🗺️", layout="wide")

# Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
data_path = os.path.join(current_dir, "..", "data", "processed_data.csv")

if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🗺️ Geographic Inclusion Coverage")

# 2. Data Load (FIXED)
try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error(f"Data file nahi mili! Path: {data_path}")
    st.stop()

# 3. State Coordinates
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
    "Haryana": {"lat": 29.0588, "lon": 76.0856}
}

# 4. Map Data Prep
state_df = df.groupby("State")[["Enrolments", "Updates"]].sum().reset_index()
state_df["lat"] = state_df["State"].map(lambda x: state_coords.get(x, {}).get("lat"))
state_df["lon"] = state_df["State"].map(lambda x: state_coords.get(x, {}).get("lon"))
map_data = state_df.dropna(subset=["lat", "lon"])

# 5. Plot Map
fig = px.scatter_mapbox(
    map_data, lat="lat", lon="lon", size="Enrolments", color="Updates",
    color_continuous_scale="Viridis", size_max=60, zoom=4,
    center={"lat": 22.5937, "lon": 78.9629},
    mapbox_style="open-street-map", hover_name="State",
    title="📍 Real-time Geographic Penetration"
)
st.plotly_chart(fig, use_container_width=True)

# 6. Data Table
with st.expander("📍 View State-wise Data Table"):
    st.dataframe(state_df[["State", "Enrolments", "Updates"]].sort_values(by="Enrolments", ascending=False), use_container_width=True)