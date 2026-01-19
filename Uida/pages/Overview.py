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
    return df

# Logo Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

st.title("🎯 Strategic Performance Signals")

# 2. Data Load
df = load_data()

if df is None:
    st.error("🚨 Waiting for team data...")
    st.stop()

# --- 3. SIDEBAR FILTERS ---
st.sidebar.header("🔍 Signal Filters")

# State Filter
if 'State' in df.columns:
    state_list = ["All India"] + sorted(df['State'].unique().tolist())
    selected_state = st.sidebar.selectbox("Region / State", state_list)
    if selected_state != "All India":
        df = df[df['State'] == selected_state]

# Risk Level Filter
if 'Risk Level' in df.columns:
    risk_options = ["All Levels"] + sorted(df['Risk Level'].unique().tolist())
    selected_risk = st.sidebar.selectbox("Risk Severity", risk_options)
    if selected_risk != "All Levels":
        df = df[df['Risk Level'] == selected_risk]

# --- 4. SUMMARY CARDS ---
total_districts = len(df)
high_risk_count = len(df[df['Risk Level'] == 'High']) if 'Risk Level' in df.columns else 0
underperf_count = len(df[df['Underperformance Flag'] == 'Yes']) if 'Underperformance Flag' in df.columns else 0
avg_megr = df['MEGR (%)'].mean() if 'MEGR (%)' in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📍 Districts Monitored", total_districts)
col2.metric("🔥 High Risk Areas", high_risk_count, delta="Action Needed", delta_color="inverse")
col3.metric("📉 Underperforming", underperf_count, delta="Needs Attention", delta_color="inverse")
col4.metric("📊 Avg MEGR", f"{avg_megr:.1f}%")

st.divider()

# --- 5. MAIN DECISION TABLE ---
st.subheader("📋 District-wise Performance Signals")

# Updated column list to include 'Latest Month'
required_columns = ['State', 'District', 'Latest Month', 'MEGR (%)', 'Volatility Level', 'Underperformance Flag', 'Risk Level']
missing_cols = [c for c in required_columns if c not in df.columns]

if not missing_cols:
    # Filter dataset
    display_df = df[required_columns].sort_values(by="MEGR (%)", ascending=True)

    # VISUAL CONFIGURATION
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "State": st.column_config.TextColumn("State"),
            "District": st.column_config.TextColumn("District"),
            
            # New Column Config
            "Latest Month": st.column_config.TextColumn(
                "Reporting Period",
                help="The month for which data is being displayed",
            ),
            
            "MEGR (%)": st.column_config.ProgressColumn(
                "MEGR Performance",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            ),
            "Risk Level": st.column_config.SelectboxColumn(
                "Risk Status",
                options=["High", "Medium", "Low"], 
                required=True,
            ),
            "Underperformance Flag": st.column_config.TextColumn(
                "Flag",
                validate="^(Yes|No)$"
            )
        }
    )
else:
    st.warning(f"⚠️ Waiting for columns: {', '.join(missing_cols)}")
    st.info("Please ask the team to ensure column names match exactly.")

# --- 6. VISUAL CONTEXT ---
col_viz1, col_viz2 = st.columns(2)

if 'Risk Level' in df.columns:
    with col_viz1:
        st.markdown("### 🚨 Risk Distribution")
        risk_counts = df['Risk Level'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        fig_risk = px.pie(risk_counts, values='Count', names='Risk Level', 
                         color='Risk Level', 
                         color_discrete_map={'High':'red', 'Medium':'orange', 'Low':'green'})
        st.plotly_chart(fig_risk, use_container_width=True)

if 'Volatility Level' in df.columns:
    with col_viz2:
        st.markdown("### 🌊 Volatility Spread")
        st.bar_chart(df['Volatility Level'].value_counts())