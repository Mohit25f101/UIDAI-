import streamlit as st
import pandas as pd
import plotly.express as px
import os

#1. Page config
st.set_page_config(page_title=" AI Forecasting", page_icon="🔮", layout="wide")

# Logo fix (Check karke lagayenge)
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🔮 AI-Powered Enrolment Forecasting")
st.markdown("Yeh system **Historical Data** ko padh kar aane wale waqt ki **Predictions** karta hai, taaki hum apne resources ko behtar plan kar sakein.")

#2. Data Load
try:
    df=pd.read_csv('data/processed_data.csv')
    #Date column ko datetime me convert kar lo
    df['Date'] = pd.to_datetime(df['Date'])
except:
    st.error("Data missing! Pehle data generate karo.")
    st.stop()

#3.Future Data Prepare karo
# Humne dummy generator mein 'Forecast' column bana rakha hai
daily_data = df.groupby("Date")[["Enrolments", "Forecast"]].sum().reset_index()

#4. Big Numbers(Prediction se judi)
current_avg = daily_data['Enrolments'].mean()
predicted_avg = daily_data['Forecast'].mean()
growth = ((predicted_avg - current_avg) / current_avg) * 100

col1, col2, col3 = st.columns(3)
col1.metric("Current Daily Avg", f"{int(current_avg):,}")
col2.metric("Predicted Next Month Avg", f"{int(predicted_avg):,}")
col3.metric("Expected Growth", f"{growth:.1f} %", delta_color="normal")

st.divider()

#5. The Prediction Chart 📈
st.subheader("📈 Actual vs Predicted Enrolments")

#Graph banate hain(Giving shape to data)
chart_data = daily_data.melt(id_vars=["Date"], var_name="Type", value_name="Count")
fig = px.line(
    chart_data,
    x="Date",
    y="Count",
    color="Type",
    markers=True,
    title="AI Projection Model",
    color_discrete_map={"Enrolments": "blue", "Forecast": "orange"} # Blue = real, Orange = Predict
)

st.plotly_chart(fig, use_container_width=True)

#6. Recommendation Box
st.info("💡 **AI Suggestion:** Agle mahine demand badhne wali hai. Staff aur Machines increase karein.")