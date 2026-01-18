import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Config
st.set_page_config(page_title="Anomaly Detection", page_icon="🚨", layout="wide")

# Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
data_path = os.path.join(current_dir, "..", "data", "processed_data.csv")

if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🚨 Anomaly Detection System")
st.markdown("**AI Rules** use karke wo data pakadta hai jo normal nahi lag raha.")

# 2. Data Load (FIXED)
try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error(f"Data file nahi mili! Path: {data_path}")
    st.stop()

# 3. Filter Anomalies
if 'Is_Anomaly' in df.columns:
    anomalies = df[df['Is_Anomaly'] == True]
else:
    st.error("Data me 'Is_Anomaly' column nahi hai.")
    st.stop()

# 4. Metrics
col1, col2 = st.columns(2)
col1.error(f"⚠️ Total Anomalies Detected: {len(anomalies)}")
col2.metric("Anomaly Rate", f"{(len(anomalies)/len(df))*100:.2f} %")

st.divider()

# 5. Scatter Plot
st.subheader("🔍 Visualizing the Outliers")
fig = px.scatter(
    df, x="Enrolments", y="Updates", color="Is_Anomaly",
    color_discrete_map={True: "red", False: "green"},
    hover_data=["District", "State", "Date"],
    title="Normal vs Suspicious Activity"
)
st.plotly_chart(fig, use_container_width=True)

# 6. Table & Download
st.subheader("📋 Detailed Anomaly Report")
st.dataframe(anomalies[["Date", "State", "District", "Enrolments", "Updates"]], use_container_width=True, hide_index=True)

csv = anomalies.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Suspicious List", csv, "uidai_anomalies.csv", "text/csv")