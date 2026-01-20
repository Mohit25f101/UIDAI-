import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Page Configuration
st.set_page_config(page_title="Strategic Overview", page_icon="🎯", layout="wide")

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
    
    # Fix Date
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
    return df

# Logo Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🎯 Strategic Performance Overview")

# 2. Data Load
df = load_data()

if df is None:
    st.error("🚨 Waiting for data...")
    st.stop()

# --- 3. SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")

if 'State' in df.columns:
    state_list = ["All India"] + sorted(df['State'].unique().tolist())
    selected_state = st.sidebar.selectbox("Region / State", state_list)
    if selected_state != "All India":
        df = df[df['State'] == selected_state]

# --- 4. KEY METRICS ---
# Check if we have strategic columns
has_strategy = 'Risk Level' in df.columns

col1, col2, col3, col4 = st.columns(4)

# Calculate Metrics
total = len(df)
if has_strategy:
    high_risk = len(df[df['Risk Level'] == 'High'])
    underperf = len(df[df['Underperformance Flag'] == 'Yes'])
    avg_megr = df['MEGR (%)'].mean()
    
    col1.metric("📍 Districts Monitored", total)
    col2.metric("🔥 High Risk Areas", high_risk, delta="Action Needed", delta_color="inverse")
    col3.metric("📉 Underperforming", underperf, delta="Attention", delta_color="inverse")
    col4.metric("📊 Avg MEGR", f"{avg_megr:.1f}%")
else:
    col1.metric("Selected Records", total)
    col2.metric("Total Enrolments", f"{df['Enrolments'].sum():,}")
    col3.metric("Avg Updates", f"{int(df['Updates'].mean()):,}")

st.divider()

# --- 5. STRATEGIC SIGNALS TABLE ---
if has_strategy:
    st.subheader("📋 District-wise Performance Signals")
    
    # Display Table
    required_cols = ['State', 'District', 'Latest Month', 'MEGR (%)', 'Volatility Level', 'Underperformance Flag', 'Risk Level']
    available_cols = [c for c in required_cols if c in df.columns]
    
    st.dataframe(
        df[available_cols].sort_values(by="MEGR (%)", ascending=True),
        use_container_width=True,
        hide_index=True,
        column_config={
            "MEGR (%)": st.column_config.ProgressColumn("MEGR", format="%.1f%%", min_value=-100, max_value=100),
            "Risk Level": st.column_config.SelectboxColumn("Risk", options=["High", "Medium", "Low"], required=True),
            "Underperformance Flag": st.column_config.TextColumn("Flag", validate="^(Yes|No)$")
        }
    )
    st.divider()

# --- 6. VISUAL CHARTS (Risk & Volatility) ---
# Now we force these to show if the columns exist
col_viz1, col_viz2 = st.columns(2)

if 'Risk Level' in df.columns:
    with col_viz1:
        st.markdown("### 🚨 Risk Distribution")
        risk_counts = df['Risk Level'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        fig_risk = px.pie(risk_counts, values='Count', names='Risk Level', 
                         color='Risk Level', 
                         color_discrete_map={'High':'red', 'Medium':'orange', 'Low':'green'},
                         hole=0.4)
        st.plotly_chart(fig_risk, use_container_width=True)

if 'Volatility Level' in df.columns:
    with col_viz2:
        st.markdown("### 🌊 Volatility Spread")
        # Bar chart for Volatility
        vol_counts = df['Volatility Level'].value_counts().reset_index()
        vol_counts.columns = ['Volatility Level', 'Count']
        fig_vol = px.bar(vol_counts, x='Volatility Level', y='Count',
                         color='Volatility Level',
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_vol, use_container_width=True)

# --- 7. STANDARD CHARTS (Enrolment Trends) ---
# These will show below the risk charts
st.divider()
col_chart1, col_chart2 = st.columns(2)

# Chart 1: Daily/Monthly Trend
if 'Date' in df.columns:
    with col_chart1:
        st.subheader(f"📅 Enrolment Volume")
        daily_trend = df.groupby("Date")[["Enrolments", "Updates"]].sum().reset_index()
        fig_line = px.line(daily_trend, x="Date", y=["Enrolments", "Updates"],
                        markers=True,
                        color_discrete_sequence=["#ffaa00", "#0088ff"])
        st.plotly_chart(fig_line, use_container_width=True)

# Chart 2: Top Districts
if 'District' in df.columns:
    with col_chart2:
        st.subheader(f"🏙️ Top 10 Districts")
        district_data = df.groupby("District")['Enrolments'].sum().reset_index().sort_values(by="Enrolments", ascending=False)
        fig_bar = px.bar(district_data.head(10), x="District", y="Enrolments",
                        color="Enrolments", color_continuous_scale="Oranges")
        st.plotly_chart(fig_bar, use_container_width=True)