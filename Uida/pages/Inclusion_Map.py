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
    # Search for the processed file in likely locations
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

# UI Header
st.title("🗺️ Real-Time Geographic Inclusion Map")
st.markdown("Live tracking of enrolment centers using **Hybrid Geospatial Intelligence**.")

df = load_data()

if df is None:
    st.error("🚨 Data not found. Please ensure 'processed_data.csv' exists.")
    st.stop()

# ==============================================================================
# 📍 THE REAL GPS ENGINE (Coordinates for YOUR Districts)
# ==============================================================================

# 1. Precise District Coordinates 
district_coords = {
    "Prayagraj": {"lat": 25.4358, "lon": 81.8463},
    "Varanasi": {"lat": 25.3176, "lon": 82.9739},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462},
    "Gurgaon": {"lat": 28.4595, "lon": 77.0266},
    "Rupnagar": {"lat": 30.9664, "lon": 76.5331},
    "Tehri Garhwal": {"lat": 30.3800, "lon": 78.4800},
    "Kargil": {"lat": 34.5539, "lon": 76.1349},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Ahilyanagar": {"lat": 19.0952, "lon": 74.7496},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Darjeeling": {"lat": 27.0410, "lon": 88.2663},
    "Patna": {"lat": 25.5941, "lon": 85.1376},
    "Anjaw": {"lat": 27.9300, "lon": 96.8000},
    "Dima Hasao": {"lat": 25.5000, "lon": 93.0000},
    "Bangalore": {"lat": 12.9716, "lon": 77.5946},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867}
}

# 2. Fallback State Coordinates
state_coords = {
    "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462},
    "Maharashtra": {"lat": 19.7515, "lon": 75.7139},
    "Bihar": {"lat": 25.0961, "lon": 85.3131},
    "West Bengal": {"lat": 22.9868, "lon": 87.8550},
    "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569},
    "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569},
    "Rajasthan": {"lat": 27.0238, "lon": 74.2179},
    "Karnataka": {"lat": 15.3173, "lon": 75.7139},
    "Gujarat": {"lat": 22.2587, "lon": 71.1924},
    "Andhra Pradesh": {"lat": 15.9129, "lon": 79.7400},
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Punjab": {"lat": 31.1471, "lon": 75.3412},
    "Haryana": {"lat": 29.0588, "lon": 76.0856},
    "Uttarakhand": {"lat": 30.0668, "lon": 79.0193},
    "Ladakh": {"lat": 34.1526, "lon": 77.5770},
    "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278},
    "Assam": {"lat": 26.2006, "lon": 92.9376},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794}
}

# --- LOGIC: HYBRID MAPPING ---
def get_lat(row):
    if row['District'] in district_coords:
        return district_coords[row['District']]['lat']
    elif row['State'] in state_coords:
        return state_coords[row['State']]['lat']
    return None

def get_lon(row):
    if row['District'] in district_coords:
        return district_coords[row['District']]['lon']
    elif row['State'] in state_coords:
        return state_coords[row['State']]['lon']
    return None

# --- PROCESSING ---
if 'District' in df.columns and 'State' in df.columns:
    # --- FIX: Changed 'Risk Level' to 'Risk_Level' to match your data schema ---
    risk_col = 'Risk_Level' if 'Risk_Level' in df.columns else 'Risk Level'
    
    map_df = df.groupby(['State', 'District']).agg({
        'Enrolments': 'sum',
        risk_col: 'first' 
    }).reset_index()

    # Apply GPS
    map_df['lat'] = map_df.apply(get_lat, axis=1)
    map_df['lon'] = map_df.apply(get_lon, axis=1)
    map_df = map_df.dropna(subset=['lat', 'lon'])

    # --- VISUALIZATION ---
    fig = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        size="Enrolments",
        color=risk_col,
        color_discrete_map={"High Risk": "#FF0000", "Medium Risk": "#FFA500", "Low Risk": "#008000"},
        hover_name="District",
        hover_data={"State": True, "Enrolments": True, "lat": False, "lon": False},
        size_max=25,
        zoom=3.8,
        center={"lat": 22.5937, "lon": 78.9629},
        mapbox_style="open-street-map",
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # --- STATS ---
    c1, c2, c3 = st.columns(3)
    c1.info(f"📍 Districts Mapped: **{len(map_df)}**")
    c2.error(f"🔴 High Risk Zones: **{len(map_df[map_df[risk_col]=='High Risk'])}**")
    c3.success(f"🟢 Stable Zones: **{len(map_df[map_df[risk_col]=='Low Risk'])}**")
else:
    st.warning("⚠️ Data missing 'District' or 'State' columns.")