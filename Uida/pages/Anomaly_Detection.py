import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Config
st.set_page_config(page_title="Anomaly Detection", page_icon="🚨", layout="wide")

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
    if 'Is_Anomaly' in df.columns:
        df['Is_Anomaly'] = df['Is_Anomaly'].astype(str).str.lower() == 'true'
    return df

# UI Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🚨 Anomaly Detection System")
st.markdown("**AI Rules** are used to detect statistical outliers in enrolment data.")

# 2. Data Load
df = load_data()

if df is None:
    st.error("🚨 Data file missing! Waiting for input...")
    st.stop()

# 3. Filter Anomalies
if 'Is_Anomaly' in df.columns:
    anomalies = df[df['Is_Anomaly'] == True]
else:
    st.error("⚠️ The 'Is_Anomaly' column is missing from the data.")
    st.stop()

# 4. Metrics
col1, col2 = st.columns(2)
col1.error(f"⚠️ Total Anomalies Detected: {len(anomalies)}")
if len(df) > 0:
    col2.metric("Anomaly Rate", f"{(len(anomalies)/len(df))*100:.2f} %")

st.divider()

# 5. Scatter Plot
st.subheader("🔍 Visualizing the Outliers")
# Ensure columns exist before plotting
required_cols = ["Enrolments", "Updates", "Is_Anomaly"]
if all(col in df.columns for col in required_cols):
    fig = px.scatter(
        df, x="Enrolments", y="Updates", color="Is_Anomaly",
        color_discrete_map={True: "red", False: "green"},
        hover_data=["District", "State", "Date"] if "District" in df.columns else None,
        title="Normal vs Suspicious Activity"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Cannot plot graph: Enrolments or Updates columns are missing.")

# 6. Table & Download
st.subheader("📋 Detailed Anomaly Report")
display_cols = [c for c in ["Date", "State", "District", "Enrolments", "Updates"] if c in anomalies.columns]
st.dataframe(anomalies[display_cols], use_container_width=True, hide_index=True)

csv = anomalies.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Suspicious List", csv, "uidai_anomalies.csv", "text/csv")