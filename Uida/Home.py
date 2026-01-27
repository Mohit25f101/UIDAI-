"""
Enhanced Home Page - UIDAI Dashboard
Features: Calendar filter, AI insights, improved metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="UIDAI Dashboard - Home",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .alert-card {
        background: #ff6b6b;
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
    }
    .success-card {
        background: #51cf66;
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
    }
    .info-banner {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-size: 18px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    paths = [
        os.path.join(current_dir, "data", "processed_data.csv"),
        os.path.join(current_dir, "..", "data", "processed_data.csv"),
        "data/processed_data.csv"
    ]
    
    for path in paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            return df
    return None

# Logo
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

# Main title
st.markdown("""
    <div class="info-banner">
        🇮🇳 Aadhaar Enrolment Intelligence System - Real-Time Analytics
    </div>
""", unsafe_allow_html=True)

# Load data
df = load_data()

if df is None:
    st.error("🚨 Data file not found! Please run the data processor first.")
    st.stop()

# ====================== SIDEBAR FILTERS ======================
st.sidebar.title("🔍 Filters & Controls")

# Date Range Filter (Calendar)
st.sidebar.subheader("📅 Select Date Range")
if 'Date' in df.columns:
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    # Handle single-day data case gracefully
    if min_date == max_date:
        st.sidebar.warning(f"⚠️ Data contains only one date: {min_date}")
        start_date = min_date
        end_date = max_date
    else:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input(
                "From",
                value=min_date,
                min_value=min_date,
                max_value=max_date
            )
        with col2:
            end_date = st.date_input(
                "To",
                value=max_date,
                min_value=min_date,
                max_value=max_date
            )
    
    # Filter data by date range
    df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    
    if min_date != max_date:
        st.sidebar.info(f"📊 Showing data from {start_date} to {end_date}")

# State Filter
if 'State' in df.columns:
    state_options = ["All India"] + sorted(df['State'].unique().tolist())
    selected_state = st.sidebar.selectbox("🗺️ Select State", state_options)
    
    if selected_state != "All India":
        df = df[df['State'] == selected_state]

# Risk Level Filter
if 'Risk_Level' in df.columns:
    risk_options = ["All Levels"] + sorted(df['Risk_Level'].unique().tolist())
    selected_risk = st.sidebar.selectbox("⚠️ Risk Level", risk_options)
    
    if selected_risk != "All Levels":
        df = df[df['Risk_Level'] == selected_risk]

# Priority Filter
if 'Priority' in df.columns:
    priority_options = ["All Priorities"] + sorted(df['Priority'].unique().tolist())
    selected_priority = st.sidebar.selectbox("🎯 Priority", priority_options)
    
    if selected_priority != "All Priorities":
        df = df[df['Priority'] == selected_priority]

st.sidebar.divider()
st.sidebar.success(f"✅ {len(df)} records loaded")

# Quick Stats in Sidebar
if len(df) > 0:
    st.sidebar.subheader("📈 Quick Stats")
    st.sidebar.metric("States Covered", df['State'].nunique() if 'State' in df.columns else 0)
    st.sidebar.metric("Districts", df['District'].nunique() if 'District' in df.columns else 0)
    if 'Is_Anomaly' in df.columns:
        anomaly_pct = (df['Is_Anomaly'].sum() / len(df) * 100)
        st.sidebar.metric("Anomaly Rate", f"{anomaly_pct:.1f}%")

# ====================== MAIN DASHBOARD ======================

# AI Executive Summary
st.markdown("### 🤖 AI Executive Summary")

if len(df) > 0:
    total_districts = len(df)
    high_risk_count = len(df[df['Risk_Level'] == 'High Risk']) if 'Risk_Level' in df.columns else 0
    anomaly_count = df['Is_Anomaly'].sum() if 'Is_Anomaly' in df.columns else 0
    
    # Determine status
    if high_risk_count > total_districts * 0.2:
        status = "⚠️ CRITICAL"
        color = "error"
    elif high_risk_count > total_districts * 0.1:
        status = "⚡ ATTENTION NEEDED"
        color = "warning"
    else:
        status = "✅ STABLE"
        color = "success"
    
    # Generate summary
    summary = f"""
    **System Status: {status}**
    
    Monitoring **{total_districts}** districts across the selected period.
    - **{high_risk_count}** districts flagged as High Risk ({high_risk_count/total_districts*100:.1f}%)
    - **{anomaly_count}** anomalies detected requiring immediate review
    """
    
    if 'State' in df.columns and high_risk_count > 0:
        top_risk_state = df[df['Risk_Level'] == 'High Risk']['State'].value_counts().head(1)
        if not top_risk_state.empty:
            summary += f"\n- 🎯 **Priority State**: {top_risk_state.index[0]} ({top_risk_state.values[0]} high-risk districts)"
    
    if color == "error":
        st.error(summary)
    elif color == "warning":
        st.warning(summary)
    else:
        st.success(summary)
    
    # Download buttons
    col_dl1, col_dl2, col_dl3 = st.columns([2, 1, 1])
    
    with col_dl2:
        if 'Risk_Level' in df.columns:
            risk_report = df[df['Risk_Level'] == 'High Risk']
            if len(risk_report) > 0:
                csv = risk_report.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Risk Report",
                    data=csv,
                    file_name=f"high_risk_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )
    
    with col_dl3:
        if 'Is_Anomaly' in df.columns:
            anomaly_report = df[df['Is_Anomaly'] == True]
            if len(anomaly_report) > 0:
                csv = anomaly_report.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Anomalies",
                    data=csv,
                    file_name=f"anomalies_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

st.divider()

# ====================== KEY METRICS ======================
st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_enrolments = df['Enrolments'].sum() if 'Enrolments' in df.columns else 0
    avg_enrolments = df['Enrolments'].mean() if 'Enrolments' in df.columns else 0
    st.metric(
        "Total Enrolments",
        f"{total_enrolments:,}",
        delta=f"Avg: {avg_enrolments:,.0f}/district"
    )

with col2:
    total_updates = df['Updates'].sum() if 'Updates' in df.columns else 0
    update_rate = (total_updates / total_enrolments * 100) if total_enrolments > 0 else 0
    st.metric(
        "Updates Processed",
        f"{total_updates:,}",
        delta=f"{update_rate:.1f}% rate"
    )

with col3:
    if 'Risk_Level' in df.columns:
        critical_alerts = len(df[df['Risk_Level'] == 'High Risk'])
        st.metric(
            "Critical Alerts",
            critical_alerts,
            delta="Needs Action" if critical_alerts > 0 else "All Clear",
            delta_color="inverse" if critical_alerts > 0 else "normal"
        )
    else:
        st.metric("Critical Alerts", "N/A")

with col4:
    if 'Confidence_Score' in df.columns:
        avg_confidence = df['Confidence_Score'].mean()
        st.metric(
            "Avg Confidence",
            f"{avg_confidence:.1f}%",
            delta="System Health"
        )
    else:
        st.metric("System Health", "N/A")

st.divider()

# ====================== VISUALIZATIONS ======================
st.subheader("📈 Trend Analysis")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("#### 📅 Daily Enrolment Trends")
    if 'Date' in df.columns and 'Enrolments' in df.columns:
        daily_data = df.groupby('Date')[['Enrolments', 'Updates']].sum().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_data['Date'],
            y=daily_data['Enrolments'],
            name='Enrolments',
            mode='lines+markers',
            line=dict(color='#4facfe', width=3),
            fill='tozeroy'
        ))
        fig.add_trace(go.Scatter(
            x=daily_data['Date'],
            y=daily_data['Updates'],
            name='Updates',
            mode='lines+markers',
            line=dict(color='#f093fb', width=2)
        ))
        
        fig.update_layout(
            hovermode='x unified',
            height=350,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Date or Enrolments data not available")

with col_chart2:
    st.markdown("#### 🗺️ State-wise Distribution")
    if 'State' in df.columns and 'Enrolments' in df.columns:
        state_data = df.groupby('State')['Enrolments'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig = px.bar(
            state_data,
            x='Enrolments',
            y='State',
            orientation='h',
            color='Enrolments',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("State or Enrolments data not available")

st.divider()

# ====================== RISK & PERFORMANCE ======================
col_risk1, col_risk2 = st.columns(2)

with col_risk1:
    st.markdown("#### ⚠️ Risk Distribution")
    if 'Risk_Level' in df.columns:
        risk_data = df['Risk_Level'].value_counts().reset_index()
        risk_data.columns = ['Risk Level', 'Count']
        
        fig = px.pie(
            risk_data,
            values='Count',
            names='Risk Level',
            color='Risk Level',
            color_discrete_map={'High Risk': '#ff6b6b', 'Medium Risk': '#ffd43b', 'Low Risk': '#51cf66'},
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Risk Level data not available")

with col_risk2:
    st.markdown("#### 🎯 Priority Actions")
    if 'Priority' in df.columns:
        priority_data = df['Priority'].value_counts().reset_index()
        priority_data.columns = ['Priority', 'Count']
        
        fig = px.bar(
            priority_data,
            x='Priority',
            y='Count',
            color='Priority',
            color_discrete_map={'High': '#ff6b6b', 'Medium': '#ffd43b', 'Low': '#51cf66'}
        )
        fig.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Priority data not available")

st.divider()

# ====================== DATA TABLE ======================
with st.expander("📋 View Detailed Data Table", expanded=False):
    display_cols = [col for col in ['State', 'District', 'Date', 'Enrolments', 'Updates', 
                                     'Risk_Level', 'Priority', 'MEGR', 'Anomaly_Score'] 
                    if col in df.columns]
    
    st.dataframe(
        df[display_cols].sort_values('Date', ascending=False),
        use_container_width=True,
        hide_index=True
    )

# Footer
st.markdown("---")
st.caption("🇮🇳 Aadhaar Enrolment Intelligence System | Powered by AI Analytics | Real-time Monitoring")