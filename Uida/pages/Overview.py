import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Setting
st.set_page_config(page_title="Enrolment Overview", page_icon="📊", layout="wide")

# Path Setup (GPS)
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
data_path = os.path.join(current_dir, "..", "data", "processed_data.csv")

# Logo
if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("📊 National Enrolment Trends")

# 2. Data Load (FIXED)
try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    st.error(f"Data file nahi mili! Path check karo: {data_path}")
    st.stop()

# 3. Sidebar Filters
st.sidebar.title("Filters")
selected_state = st.sidebar.selectbox("Select State", ["All India"] + df['State'].unique().tolist())

# Filter Logic
if selected_state != "All India":
    filtered_df = df[df['State'] == selected_state]
else:
    filtered_df = df

# 4. Scoreboard
col1, col2, col3 = st.columns(3)
col1.metric("Selected Records", len(filtered_df))
col2.metric("Total Enrolments", f"{filtered_df['Enrolments'].sum():,}")
col3.metric("Avg Daily Updates", f"{int(filtered_df['Updates'].mean()):,}")

st.divider()

# 5. Chart 1: Trends
st.subheader(f"📅 Enrolment Trend - {selected_state}")
daily_trend = filtered_df.groupby("Date")[["Enrolments", "Updates"]].sum().reset_index()
fig_line = px.line(daily_trend, x="Date", y=["Enrolments", "Updates"],
                  markers=True, title="Daily Enrolments & Updates",
                  color_discrete_sequence=["#ffaa00", "#0088ff"])
st.plotly_chart(fig_line, use_container_width=True)

# 6. Chart 2: Top Districts
st.subheader(f"🏙️ District Performance - {selected_state}")
district_data = filtered_df.groupby("District")['Enrolments'].sum().reset_index().sort_values(by="Enrolments", ascending=False)
fig_bar = px.bar(district_data.head(10), x="District", y="Enrolments",
                color="Enrolments", color_continuous_scale="Oranges",
                title="Top 10 Districts")
st.plotly_chart(fig_bar, use_container_width=True)