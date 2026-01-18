import streamlit as st
import pandas as pd
import plotly.express as px
import os

#1. Page setup
st.set_page_config(page_title="Anomaly Detection", page_icon="🚨", layout="wide")

# Logo fix (Check karke lagayenge)
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🚨 Anomaly Detection System")
st.markdown("**AI Rules** use karke wo data pakadta hai jo normal nahi lag raha (fraud/Error).")

#2. Data Load
try:
    df=pd.read_csv('data/processed_data.csv')
except:
    st.error("Data missing! Generate Karo pehle.")
    st.stop()

#3.Gadbad Data Dhundo (Filter logic)
# Dummy data mei is Anomaly column bna rekha hai 
anomalies = df[df['Is_Anomaly'] == True]
normal_data = df[df['Is_Anomaly'] == False]

#4.Top Alerts (Danger RED)
col1, col2 = st.columns(2)
col1.error(f"⚠️ Total Anomalies Detected: {len(anomalies)}")
col2.metric("Anomaly Rate", f"{(len(anomalies)/len(df))*100:.2f} %")

st.divider()

#5. visual proof(scatter plot)
st.subheader("🔍 Visualizing the Outliers")
st.caption("jo lal Dots(Red) hain, wo anomalies hain. Wo baaki data se alag behave kar rahe hain.")

#Graph : X-axis: Enrolments, Y-axis: Updates
fig = px.scatter(
    df,
    x="Enrolments",
    y="Updates",
    color="Is_Anomaly", # Color alag karo (T/F)
    hover_data=["District", "State", "Date"],
    color_discrete_map={True: "red", False: "green"}, # True=Red, False=Green
    title="Normal vs Suspicious Activity"
)
st.plotly_chart(fig, use_container_width=True)

#6. The "Blacklist" Table
st.subheader("📋 Detailed Anomaly Report")
st.write("District in which have Problem(Gadbad hai):")

#Table dikhao par style ke saath
st.dataframe(
    anomalies[["Date", "State", "District", "Enrolments", "Updates"]],
    use_container_width=True,
    hide_index=True
)

#Download Button (officer ke liye)
csv = anomalies.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Suspicious List",
    data=csv,
    file_name='uidai_anomalies.csv',
    mime='text/csv',
)

