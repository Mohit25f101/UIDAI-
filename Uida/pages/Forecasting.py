import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Config
st.set_page_config(page_title="AI Forecasting", page_icon="🔮", layout="wide")

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

st.title("🔮 AI-Powered Enrolment Forecasting")

# 2. Data Load
df = load_data()

if df is None:
    st.error("🚨 Data file missing!")
    st.stop()

# 3. Forecast Data Check
if 'Forecast' not in df.columns:
    st.error("⚠️ 'Forecast' column is missing! Please check the data source.")
    st.stop()

# Group by Date
daily_data = df.groupby("Date")[["Enrolments", "Forecast"]].sum().reset_index()

# 4. Metrics
current_avg = daily_data['Enrolments'].mean()
predicted_avg = daily_data['Forecast'].mean()
growth = ((predicted_avg - current_avg) / current_avg) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Current Daily Avg", f"{int(current_avg):,}")
col2.metric("Predicted Next Month Avg", f"{int(predicted_avg):,}")
col3.metric("Expected Growth", f"{growth:.1f} %")

st.divider()

# 5. Chart
st.subheader("📈 Actual vs Predicted Enrolments")
chart_data = daily_data.melt(id_vars=["Date"], var_name="Type", value_name="Count")
fig = px.line(chart_data, x="Date", y="Count", color="Type", markers=True,
              color_discrete_map={"Enrolments": "blue", "Forecast": "orange"})
st.plotly_chart(fig, use_container_width=True)

st.info("💡 **AI Insight:** Enrolment demand is expected to rise in the upcoming month.")