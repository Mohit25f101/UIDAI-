import streamlit as st
import pandas as pd
import plotly.express as px
import os

#1. Page Config
st.set_page_config(page_title="Inclusion Map", page_icon="🗺️", layout="wide")

# Logo fix (Check karke lagayenge)
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🗺️ Geographic Inclusin Coverage")  # Main title
st.markdown ("Yeh map dikhata hai ki kis state mein **Enrolments (Size)** aur **Updates (color)** kaise distribute hua hai.")

#2. Data Load Karo
try:
    df = pd.read_csv('data/processed_data.csv')
except:
    st.error("Data missing!")
    st.stop()

#3. India ke coordinates(long.&lat. of state )
#Not GPS data toh manually state ke location dal di
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

#4. Data Prepare Karo
# State ke hisaab se total nikalo
state_df =df.groupby("State")[["Enrolments", "Updates"]].sum().reset_index()

#DataFrame mein Lat/Lon add karo
state_df["lat"] = state_df["State"].map(lambda x: state_coords.get(x, {}).get("lat"))
state_df["lon"] = state_df["State"].map(lambda x: state_coords.get(x, {}).get("lon"))

#Jin states coordinate nahi found, unha remove ker diya (for NOW!)[Safety pupose]
map_data = state_df.dropna(subset=["lat", "lon"])

#5. Super MAP 
fig = px.scatter_mapbox(
    map_data,
    lat="lat",
    lon="lon",
    size="Enrolments",  #kitne naye Aadhar bane
    color="Updates",    #kitne update hue
    color_continuous_scale="Viridis",
    center={"lat": 22.5937, "lon": 78.9629}, #India center
    size_max=60,
    zoom=4,
    mapbox_style="open-street-map",
    hover_name="State", 
    hover_data={"Enrolments": True, "Updates": True, "lat": False, "lon": False},
    title="📍 Real-time Geographic Penetration"
)

#Map on screen\
st.plotly_chart(fig, use_container_width=True)

#6. DATA TABLE below
with st.expander("📍 View State-wise Data Table"):
    st.dataframe(state_df[["State", "Enrolments", "Updates"]].sort_values(by="Enrolments", ascending=False), use_container_width=True)