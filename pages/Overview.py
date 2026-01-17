import streamlit as st
import pandas as pd
import plotly.express as px  # Ye graph banane wala painter hai
#1. Page ki setting (Tittle aur icon)
st.set_page_config(page_title="Enrolment Overview", page_icon="📊", layout="wide")
st.logo("assets/uidai_logo.png") # Apna brand stamp

st.title("📊 National Enrolment Trends") # Page ka big headline

#2. Data load karnatry:
try:
    df = pd.read_csv('data/processed_data.csv')
except FileNotFoundError:
    #Agar Data  nahi mila toh user ko batao, crash mat hone do
    st.error("Data file nahi mili! 'processed_data.csv' check kar le.")
    st.stop() # Aage ka code mat chalana

#3. Sidebar filters(Remote)
st.sidebar.title("Filters")

#Dropdown for State selection
# Hum .tolist() use karenge jo guaranteed kaam karega
selected_state = st.sidebar.selectbox("Select State", ["All India"] + df['State'].unique().tolist())

#Filter data based on selection
if selected_state != "All India":
    filtered_df = df[df['State'] == selected_state]
else:
    filtered_df = df # see All India

#4. Scoreboard (Top Numbers)
col1, col2, col3 = st.columns(3)
col1.metric("Selected Records", len(filtered_df)) #Kitne row hain
col2.metric("Total Enrolments", f"{filtered_df['Enrolments'].sum():,}") #Total Enrolments
col3.metric("Avg Daily Updates", f"{int(filtered_df['Updates'].mean()):,}")

st.divider() # Made the line of Design

#5. CHART 1: Line chart (like trading graph)
st.subheader(f"📅 Enrolment Trend - {selected_state}")

#Putting data category Wise(Grouping)
daily_trend = filtered_df.groupby("Date")[["Enrolments", "Updates"]].sum().reset_index()

#Graph X-Y axis (NO.)
fig_line = px.line(daily_trend, x="Date", y=["Enrolments", "Updates"],  
                  markers =True, title="Daily Enrolments and Updates Over Time",
                  color_discrete_sequence=["#ffaa00", "#0088ff"]) # UIDAI ke colors (Orange/Blue)

st.plotly_chart(fig_line, use_container_width=True) # Graph on screen

#6. CHART 2: Bar Chart (Whose District is on top?)
st.subheader(f"🏙️ District Performance - {selected_state}")

#Districts total(so top one come foreword)
district_data = filtered_df.groupby("District")['Enrolments'].sum().reset_index().sort_values(by="Enrolments", ascending=False)

#Top 10 Districts ka graph 
fig_bar = px.bar(district_data.head(10), x="District", y="Enrolments", 
                color="Enrolments", color_continuous_scale="Oranges",
                title="Top 10 Districts (by Enrolments)")

st.plotly_chart(fig_bar, use_container_width=True) # Show kar diya graph