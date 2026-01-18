import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Config
st.set_page_config(page_title="AI Forecasting", page_icon="🔮", layout="wide")

# Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
data_path = os.path.join(current_dir, "..", "data", "processed_data.csv")

if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🔮 AI-Powered Enrolment Forecasting")

# 2. Data Load (FIXED)
try:
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
except FileNotFoundError:
    st.error(f"Data file nahi mili! Path: {data_path}")
    st.stop()

# 3. Forecast Data
if 'Forecast' not in df.columns:
    st.error("Forecast column missing!")
    st.stop()

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

st.info("💡 **AI Suggestion:** Agle mahine demand badhne wali hai.")