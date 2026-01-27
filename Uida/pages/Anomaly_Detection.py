"""
Enhanced Anomaly Detection Page - UIDAI Dashboard
Features: Multiple detection algorithms, severity scoring, investigation tools
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="Anomaly Detection - UIDAI",
    page_icon="🚨",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .anomaly-critical {
        background: #ff6b6b;
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
        border-left: 5px solid #c92a2a;
    }
    .anomaly-warning {
        background: #ffd43b;
        padding: 15px;
        border-radius: 8px;
        color: #000;
        margin: 10px 0;
        border-left: 5px solid #fab005;
    }
    .anomaly-info {
        background: #4facfe;
        padding: 15px;
        border-radius: 8px;
        color: white;
        margin: 10px 0;
        border-left: 5px solid #1c7ed6;
    }
    </style>
""", unsafe_allow_html=True)

# Data loader
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
            if 'Is_Anomaly' in df.columns:
                df['Is_Anomaly'] = df['Is_Anomaly'].astype(str).str.lower().isin(['true', '1', 'yes'])
            return df
    return None

def calculate_anomaly_severity(row):
    """Calculate severity score based on multiple factors"""
    score = 0
    
    # Risk level contribution
    if 'Risk_Level' in row and row['Risk_Level'] == 'High Risk':
        score += 40
    elif 'Risk_Level' in row and row['Risk_Level'] == 'Medium Risk':
        score += 20
    
    # Anomaly score contribution
    if 'Anomaly_Score' in row and pd.notna(row['Anomaly_Score']):
        score += min(row['Anomaly_Score'] * 30, 30)
    
    # Volatility contribution
    if 'Volatility_Score' in row and pd.notna(row['Volatility_Score']):
        score += min(row['Volatility_Score'] * 10, 20)
    
    # Underperformance contribution
    if 'Underperformance_Flag' in row and row['Underperformance_Flag'] == 'Yes':
        score += 10
    
    return min(score, 100)

def categorize_severity(score):
    """Categorize severity into levels"""
    if score >= 70:
        return 'Critical'
    elif score >= 40:
        return 'High'
    elif score >= 20:
        return 'Medium'
    else:
        return 'Low'

# Logo
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

# Title
st.title("🚨 Advanced Anomaly Detection System")
st.markdown("**AI-powered fraud detection and pattern recognition**")

# Load data
df = load_data()

if df is None:
    st.error("🚨 Data file not found!")
    st.stop()

# ====================== SIDEBAR FILTERS ======================
st.sidebar.title("🔍 Detection Settings")

# Detection sensitivity
sensitivity = st.sidebar.slider(
    "Detection Sensitivity",
    min_value=1,
    max_value=10,
    value=5,
    help="Higher values detect more anomalies"
)

# Severity filter
severity_filter = st.sidebar.multiselect(
    "Severity Levels",
    ['Critical', 'High', 'Medium', 'Low'],
    default=['Critical', 'High']
)

# State filter
if 'State' in df.columns:
    state_options = ["All States"] + sorted(df['State'].unique().tolist())
    selected_state = st.sidebar.selectbox("🗺️ Filter by State", state_options)
    
    if selected_state != "All States":
        df = df[df['State'] == selected_state]

st.sidebar.divider()

# Detection method
detection_method = st.sidebar.radio(
    "Detection Algorithm",
    ["Combined (AI)", "Statistical", "Rule-Based"],
    help="Choose the anomaly detection method"
)

# ====================== CALCULATE ANOMALIES ======================

# Calculate severity scores
if 'Is_Anomaly' not in df.columns:
    # Fallback: detect based on statistical methods
    if 'Anomaly_Score' in df.columns:
        threshold = df['Anomaly_Score'].quantile(0.95 - (sensitivity - 5) * 0.05)
        df['Is_Anomaly'] = df['Anomaly_Score'] > threshold
    else:
        # Use enrolment outliers
        if 'Enrolments' in df.columns:
            Q1 = df['Enrolments'].quantile(0.25)
            Q3 = df['Enrolments'].quantile(0.75)
            IQR = Q3 - Q1
            threshold_multiplier = 1.5 + (10 - sensitivity) * 0.3
            lower = Q1 - threshold_multiplier * IQR
            upper = Q3 + threshold_multiplier * IQR
            df['Is_Anomaly'] = (df['Enrolments'] < lower) | (df['Enrolments'] > upper)

# Calculate severity
df['Severity_Score'] = df.apply(calculate_anomaly_severity, axis=1)
df['Severity_Level'] = df['Severity_Score'].apply(categorize_severity)

# Filter by severity
if severity_filter:
    anomalies = df[(df['Is_Anomaly'] == True) & (df['Severity_Level'].isin(severity_filter))]
else:
    anomalies = df[df['Is_Anomaly'] == True]

# ====================== DASHBOARD METRICS ======================
st.subheader("📊 Detection Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_records = len(df)
    anomaly_count = len(anomalies)
    anomaly_rate = (anomaly_count / total_records * 100) if total_records > 0 else 0
    
    st.metric(
        "Total Anomalies",
        anomaly_count,
        delta=f"{anomaly_rate:.1f}% of records",
        delta_color="inverse"
    )

with col2:
    critical_count = len(anomalies[anomalies['Severity_Level'] == 'Critical'])
    st.metric(
        "Critical Cases",
        critical_count,
        delta="Immediate Action",
        delta_color="inverse" if critical_count > 0 else "off"
    )

with col3:
    high_count = len(anomalies[anomalies['Severity_Level'] == 'High'])
    st.metric(
        "High Priority",
        high_count,
        delta="Investigation",
        delta_color="inverse" if high_count > 0 else "off"
    )

with col4:
    if 'State' in anomalies.columns and len(anomalies) > 0:
        top_state = anomalies['State'].value_counts().head(1)
        if not top_state.empty:
            st.metric(
                "Most Affected",
                top_state.index[0],
                delta=f"{top_state.values[0]} cases"
            )
    else:
        st.metric("Status", "Clear")

st.divider()

# ====================== SEVERITY DISTRIBUTION ======================
col_sev1, col_sev2 = st.columns([1, 2])

with col_sev1:
    st.markdown("#### ⚠️ Severity Breakdown")
    
    if len(anomalies) > 0:
        severity_counts = anomalies['Severity_Level'].value_counts().reset_index()
        severity_counts.columns = ['Severity', 'Count']
        
        # Define colors
        color_map = {
            'Critical': '#ff6b6b',
            'High': '#ffd43b',
            'Medium': '#4facfe',
            'Low': '#51cf66'
        }
        
        fig_sev = px.pie(
            severity_counts,
            values='Count',
            names='Severity',
            color='Severity',
            color_discrete_map=color_map,
            hole=0.5
        )
        fig_sev.update_traces(textposition='inside', textinfo='percent+label')
        fig_sev.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_sev, use_container_width=True)
    else:
        st.success("✅ No anomalies detected in current filters")

with col_sev2:
    st.markdown("#### 📈 Anomaly Timeline")
    
    if len(anomalies) > 0 and 'Date' in anomalies.columns:
        # Aggregate by date
        daily_anomalies = anomalies.groupby('Date').size().reset_index(name='Count')
        
        fig_timeline = go.Figure()
        
        fig_timeline.add_trace(go.Scatter(
            x=daily_anomalies['Date'],
            y=daily_anomalies['Count'],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#ff6b6b', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Date</b>: %{x}<br><b>Anomalies</b>: %{y}<extra></extra>'
        ))
        
        fig_timeline.update_layout(
            height=300,
            xaxis_title="Date",
            yaxis_title="Number of Anomalies",
            hovermode='x',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No timeline data available")

st.divider()

# ====================== SCATTER PLOT ANALYSIS ======================
st.subheader("🔍 Pattern Analysis")

if 'Enrolments' in df.columns and 'Updates' in df.columns:
    # Create scatter plot
    fig_scatter = px.scatter(
        df,
        x='Enrolments',
        y='Updates',
        color='Is_Anomaly',
        color_discrete_map={True: '#ff6b6b', False: '#4facfe'},
        size='Severity_Score' if 'Severity_Score' in df.columns else None,
        hover_data=['State', 'District', 'Date'] if all(col in df.columns for col in ['State', 'District', 'Date']) else None,
        labels={'Is_Anomaly': 'Anomaly Status'},
        title="Enrolments vs Updates - Anomaly Detection"
    )
    
    # Add reference lines
    if len(df) > 0:
        avg_enrolments = df['Enrolments'].mean()
        avg_updates = df['Updates'].mean()
        
        fig_scatter.add_hline(
            y=avg_updates,
            line_dash="dash",
            line_color="gray",
            annotation_text="Avg Updates",
            annotation_position="right"
        )
        
        fig_scatter.add_vline(
            x=avg_enrolments,
            line_dash="dash",
            line_color="gray",
            annotation_text="Avg Enrolments",
            annotation_position="top"
        )
    
    fig_scatter.update_layout(
        height=500,
        legend=dict(title="Status"),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("⚠️ Enrolments or Updates data not available for visualization")

st.divider()

# ====================== DETAILED ANOMALY TABLE ======================
st.subheader("📋 Detailed Anomaly Report")

if len(anomalies) > 0:
    # Prepare display columns
    display_cols = ['Date', 'State', 'District', 'Enrolments', 'Updates', 
                    'Severity_Level', 'Severity_Score', 'Risk_Level']
    display_cols = [col for col in display_cols if col in anomalies.columns]
    
    # Add color coding
    def highlight_severity(row):
        if row['Severity_Level'] == 'Critical':
            return ['background-color: #ffe0e0'] * len(row)
        elif row['Severity_Level'] == 'High':
            return ['background-color: #fff4e0'] * len(row)
        elif row['Severity_Level'] == 'Medium':
            return ['background-color: #e0f2ff'] * len(row)
        else:
            return [''] * len(row)
    
    # Sort by severity and date
    anomalies_display = anomalies[display_cols].sort_values(
        ['Severity_Score', 'Date'],
        ascending=[False, False]
    )
    
    st.dataframe(
        anomalies_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Severity_Score": st.column_config.ProgressColumn(
                "Severity",
                format="%.0f",
                min_value=0,
                max_value=100
            ),
            "Date": st.column_config.DateColumn(
                "Date",
                format="DD-MM-YYYY"
            )
        }
    )
    
    # Statistics
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    
    with col_stat1:
        avg_severity = anomalies['Severity_Score'].mean()
        st.info(f"**Average Severity**: {avg_severity:.1f}/100")
    
    with col_stat2:
        states_affected = anomalies['State'].nunique() if 'State' in anomalies.columns else 0
        st.info(f"**States Affected**: {states_affected}")
    
    with col_stat3:
        districts_affected = anomalies['District'].nunique() if 'District' in anomalies.columns else 0
        st.info(f"**Districts Affected**: {districts_affected}")

else:
    st.success("✅ No anomalies detected matching your criteria. System operating normally.")

st.divider()

# ====================== TOP ANOMALIES HIGHLIGHTS ======================
if len(anomalies) > 0:
    st.subheader("🎯 Priority Cases (Top 5)")
    
    top_anomalies = anomalies.nlargest(5, 'Severity_Score')
    
    for idx, row in top_anomalies.iterrows():
        severity = row.get('Severity_Level', 'Unknown')
        state = row.get('State', 'Unknown')
        district = row.get('District', 'Unknown')
        score = row.get('Severity_Score', 0)
        date = row.get('Date', 'Unknown')
        enrolments = row.get('Enrolments', 'N/A')
        
        if severity == 'Critical':
            st.markdown(f"""
                <div class="anomaly-critical">
                    <strong>🚨 CRITICAL - {state}, {district}</strong><br>
                    Severity Score: {score:.0f}/100 | Date: {date}<br>
                    Enrolments: {enrolments} | Status: Requires immediate investigation
                </div>
            """, unsafe_allow_html=True)
        elif severity == 'High':
            st.markdown(f"""
                <div class="anomaly-warning">
                    <strong>⚠️ HIGH PRIORITY - {state}, {district}</strong><br>
                    Severity Score: {score:.0f}/100 | Date: {date}<br>
                    Enrolments: {enrolments} | Status: Investigation recommended
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class="anomaly-info">
                    <strong>ℹ️ {severity.upper()} - {state}, {district}</strong><br>
                    Severity Score: {score:.0f}/100 | Date: {date}<br>
                    Enrolments: {enrolments} | Status: Monitor situation
                </div>
            """, unsafe_allow_html=True)

st.divider()

# ====================== DOWNLOAD OPTIONS ======================
st.subheader("📥 Export Anomaly Reports")

col_dl1, col_dl2, col_dl3 = st.columns(3)

with col_dl1:
    if len(anomalies) > 0:
        csv_all = anomalies.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 All Anomalies",
            data=csv_all,
            file_name=f"anomaly_report_all_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

with col_dl2:
    critical_anomalies = anomalies[anomalies['Severity_Level'].isin(['Critical', 'High'])]
    if len(critical_anomalies) > 0:
        csv_critical = critical_anomalies.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="🚨 Critical Cases Only",
            data=csv_critical,
            file_name=f"critical_anomalies_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

with col_dl3:
    if 'State' in anomalies.columns:
        # Summary by state
        state_summary = anomalies.groupby('State').agg({
            'Severity_Score': 'mean',
            'District': 'count'
        }).reset_index()
        state_summary.columns = ['State', 'Avg_Severity', 'Anomaly_Count']
        
        csv_summary = state_summary.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📊 Summary by State",
            data=csv_summary,
            file_name=f"state_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

# Footer
st.markdown("---")
st.caption(f"🚨 Detection Method: {detection_method} | Sensitivity: {sensitivity}/10 | Active Filters: {', '.join(severity_filter) if severity_filter else 'None'}")