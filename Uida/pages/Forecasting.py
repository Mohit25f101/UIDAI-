"""
Enhanced Forecasting Page - UIDAI Dashboard
Features: Multiple forecast models, confidence intervals, scenario analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
import os

# Page configuration
st.set_page_config(
    page_title="AI Forecasting - UIDAI",
    page_icon="🔮",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .forecast-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .metric-container {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4facfe;
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
            return df
    return None

# Load forecast data
@st.cache_data
def load_forecast_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    forecast_files = [
        os.path.join(current_dir, "data", "uidai_multistate_forecast.csv"),
        os.path.join(current_dir, "..", "data", "uidai_multistate_forecast.csv"),
    ]
    
    for file in forecast_files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            df['month'] = pd.to_datetime(df['month'])
            return df
    return None

# Logo
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "..", "assets", "uidai_logo.png")
if os.path.exists(logo_path):
    st.logo(logo_path)

# Title
st.title("🔮 AI-Powered Enrolment Forecasting")
st.markdown("**Predictive analytics for resource planning and demand estimation**")

# Load data
df = load_data()
forecast_df = load_forecast_data()

if df is None:
    st.error("🚨 Historical data not found!")
    st.stop()

# ====================== SIDEBAR CONTROLS ======================
st.sidebar.title("🎛️ Forecast Settings")

# Forecast horizon
forecast_months = st.sidebar.slider(
    "Forecast Horizon (months)",
    min_value=1,
    max_value=6,
    value=3,
    help="Number of months to forecast into the future"
)

# State selection
if 'State' in df.columns:
    state_options = ["All India"] + sorted(df['State'].unique().tolist())
    selected_state = st.sidebar.selectbox("🗺️ Select State", state_options, key='forecast_state')
    
    if selected_state != "All India":
        df = df[df['State'] == selected_state]
        if forecast_df is not None:
            forecast_df = forecast_df[forecast_df['state'] == selected_state]

# Scenario analysis
st.sidebar.subheader("📊 Scenario Analysis")
growth_scenario = st.sidebar.radio(
    "Growth Scenario",
    ["Conservative", "Baseline", "Optimistic"],
    index=1
)

scenario_factors = {
    "Conservative": 0.85,
    "Baseline": 1.0,
    "Optimistic": 1.15
}

st.sidebar.divider()

# Confidence level
confidence_level = st.sidebar.selectbox(
    "Confidence Interval",
    [90, 95, 99],
    index=1,
    format_func=lambda x: f"{x}%"
)

# ====================== FORECAST GENERATION ======================

# Generate forecasts
if 'Date' in df.columns and 'Enrolments' in df.columns:
    # Aggregate historical data
    historical = df.groupby('Date')['Enrolments'].sum().reset_index()
    historical = historical.sort_values('Date')
    
    # Calculate trend
    if len(historical) > 1:
        # Simple moving average for trend
        window = min(7, len(historical))
        historical['MA'] = historical['Enrolments'].rolling(window=window, min_periods=1).mean()
        
        # Calculate growth rate
        recent_growth = (historical['MA'].iloc[-1] - historical['MA'].iloc[0]) / len(historical)
        
        # Generate forecast dates
        last_date = historical['Date'].max()
        forecast_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=forecast_months * 30,
            freq='D'
        )
        
        # Generate forecast
        base_value = historical['MA'].iloc[-1]
        forecast_values = []
        lower_bound = []
        upper_bound = []
        
        for i, date in enumerate(forecast_dates):
            # Trend component
            trend = base_value + (recent_growth * i)
            
            # Apply scenario factor
            forecast = trend * scenario_factors[growth_scenario]
            
            # Add seasonality (simple sine wave)
            seasonality = np.sin(2 * np.pi * i / 30) * (forecast * 0.1)
            forecast += seasonality
            
            # Calculate confidence intervals
            std_dev = historical['Enrolments'].std()
            z_scores = {90: 1.645, 95: 1.96, 99: 2.576}
            z = z_scores[confidence_level]
            margin = z * std_dev * np.sqrt(1 + i/len(historical))
            
            forecast_values.append(max(0, forecast))
            lower_bound.append(max(0, forecast - margin))
            upper_bound.append(forecast + margin)
        
        # Create forecast dataframe
        forecast_generated = pd.DataFrame({
            'Date': forecast_dates,
            'Forecast': forecast_values,
            'Lower': lower_bound,
            'Upper': upper_bound
        })

# ====================== METRICS ======================
st.subheader("📊 Forecast Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    current_avg = historical['Enrolments'].tail(30).mean()
    st.metric(
        "Current 30-Day Avg",
        f"{current_avg:,.0f}",
        help="Average daily enrolments over the last 30 days"
    )

with col2:
    if len(forecast_generated) > 0:
        forecast_avg = forecast_generated['Forecast'].head(30).mean()
        change = ((forecast_avg - current_avg) / current_avg) * 100
        st.metric(
            "Next 30-Day Forecast",
            f"{forecast_avg:,.0f}",
            delta=f"{change:+.1f}%",
            help="Predicted average for next 30 days"
        )

with col3:
    if len(forecast_generated) > 0:
        total_forecast = forecast_generated['Forecast'].sum()
        st.metric(
            f"Total ({forecast_months}mo)",
            f"{total_forecast:,.0f}",
            help=f"Total predicted enrolments over {forecast_months} months"
        )

with col4:
    if 'State_Forecast' in df.columns:
        official_forecast = df['State_Forecast'].mean()
        st.metric(
            "State Forecast",
            f"{official_forecast:,.0f}",
            help="Official state-level forecast"
        )
    else:
        st.metric(
            "Confidence",
            f"{confidence_level}%",
            help="Forecast confidence interval"
        )

st.divider()

# ====================== VISUALIZATION ======================
st.subheader("📈 Forecast Visualization")

# Create the forecast chart
fig = go.Figure()

# Historical data
fig.add_trace(go.Scatter(
    x=historical['Date'],
    y=historical['Enrolments'],
    name='Historical',
    mode='lines',
    line=dict(color='#4facfe', width=2),
    hovertemplate='<b>Date</b>: %{x}<br><b>Enrolments</b>: %{y:,.0f}<extra></extra>'
))

# Moving average
fig.add_trace(go.Scatter(
    x=historical['Date'],
    y=historical['MA'],
    name='Trend',
    mode='lines',
    line=dict(color='#f093fb', width=2, dash='dash'),
    hovertemplate='<b>Date</b>: %{x}<br><b>Trend</b>: %{y:,.0f}<extra></extra>'
))

# Forecast
fig.add_trace(go.Scatter(
    x=forecast_generated['Date'],
    y=forecast_generated['Forecast'],
    name=f'Forecast ({growth_scenario})',
    mode='lines',
    line=dict(color='#ffd43b', width=3),
    hovertemplate='<b>Date</b>: %{x}<br><b>Forecast</b>: %{y:,.0f}<extra></extra>'
))

# Confidence interval
fig.add_trace(go.Scatter(
    x=forecast_generated['Date'],
    y=forecast_generated['Upper'],
    name=f'Upper Bound ({confidence_level}%)',
    mode='lines',
    line=dict(width=0),
    showlegend=False,
    hoverinfo='skip'
))

fig.add_trace(go.Scatter(
    x=forecast_generated['Date'],
    y=forecast_generated['Lower'],
    name=f'Confidence Interval ({confidence_level}%)',
    mode='lines',
    line=dict(width=0),
    fillcolor='rgba(255, 212, 59, 0.2)',
    fill='tonexty',
    hovertemplate='<b>Date</b>: %{x}<br><b>Range</b>: %{y:,.0f}<extra></extra>'
))

# --- FIX: Replaced add_vline with add_shape to prevent Timestamp errors ---
fig.add_shape(
    type="line",
    x0=historical['Date'].max(), y0=0,
    x1=historical['Date'].max(), y1=1,
    xref="x", yref="paper",
    line=dict(color="Gray", width=2, dash="dash"),
)

fig.update_layout(
    height=500,
    hovermode='x unified',
    xaxis_title="Date",
    yaxis_title="Enrolments",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ====================== DETAILED ANALYSIS ======================
col_analysis1, col_analysis2 = st.columns(2)

with col_analysis1:
    st.markdown("#### 📊 Monthly Forecast Breakdown")
    
    # Aggregate by month
    forecast_generated['Month'] = forecast_generated['Date'].dt.to_period('M')
    monthly_forecast = forecast_generated.groupby('Month').agg({
        'Forecast': 'sum',
        'Lower': 'sum',
        'Upper': 'sum'
    }).reset_index()
    monthly_forecast['Month'] = monthly_forecast['Month'].astype(str)
    
    # Create bar chart
    fig_monthly = go.Figure()
    
    fig_monthly.add_trace(go.Bar(
        x=monthly_forecast['Month'],
        y=monthly_forecast['Forecast'],
        name='Forecast',
        marker_color='#4facfe',
        error_y=dict(
            type='data',
            symmetric=False,
            array=monthly_forecast['Upper'] - monthly_forecast['Forecast'],
            arrayminus=monthly_forecast['Forecast'] - monthly_forecast['Lower'],
            color='rgba(0,0,0,0.3)'
        )
    ))
    
    fig_monthly.update_layout(
        height=350,
        xaxis_title="Month",
        yaxis_title="Predicted Enrolments",
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig_monthly, use_container_width=True)

with col_analysis2:
    st.markdown("#### 🎯 Scenario Comparison")
    
    # Calculate all scenarios
    scenarios_data = []
    for scenario, factor in scenario_factors.items():
        forecast_generated_scenario = forecast_generated.copy()
        forecast_generated_scenario['Scenario'] = scenario
        forecast_generated_scenario['Value'] = forecast_generated_scenario['Forecast'] * (factor / scenario_factors[growth_scenario])
        scenarios_data.append(forecast_generated_scenario[['Date', 'Scenario', 'Value']])
    
    scenarios_df = pd.concat(scenarios_data)
    
    fig_scenarios = px.line(
        scenarios_df,
        x='Date',
        y='Value',
        color='Scenario',
        color_discrete_map={
            'Conservative': '#ff6b6b',
            'Baseline': '#4facfe',
            'Optimistic': '#51cf66'
        }
    )
    
    fig_scenarios.update_layout(
        height=350,
        xaxis_title="Date",
        yaxis_title="Enrolments",
        legend=dict(title="Scenario"),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    st.plotly_chart(fig_scenarios, use_container_width=True)

st.divider()

# ====================== INSIGHTS & RECOMMENDATIONS ======================
st.subheader("💡 AI-Generated Insights")

insights = []

# Growth trend
if recent_growth > 0:
    insights.append(f"📈 **Positive Growth**: The system detects an upward trend of approximately {recent_growth:.0f} enrolments per day.")
else:
    insights.append(f"📉 **Declining Trend**: The system detects a downward trend. Consider intervention strategies.")

# Peak prediction
peak_month = monthly_forecast.loc[monthly_forecast['Forecast'].idxmax(), 'Month']
peak_value = monthly_forecast['Forecast'].max()
insights.append(f"🎯 **Peak Demand**: Highest demand expected in **{peak_month}** with approximately **{peak_value:,.0f}** enrolments.")

# Resource recommendation
total_forecast = forecast_generated['Forecast'].sum()
avg_daily = total_forecast / len(forecast_generated)
centers_needed = int(avg_daily / 100)  # Assuming 100 enrolments per center per day
insights.append(f"🏢 **Resource Planning**: Based on forecast, approximately **{centers_needed}** active centers recommended.")

# Display insights
for insight in insights:
    st.info(insight)

st.divider()

# ====================== DOWNLOAD OPTIONS ======================
st.subheader("📥 Export Forecast Data")

col_dl1, col_dl2, col_dl3 = st.columns(3)

with col_dl1:
    # Daily forecast
    csv_daily = forecast_generated.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📄 Daily Forecast",
        data=csv_daily,
        file_name=f"daily_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

with col_dl2:
    # Monthly forecast
    csv_monthly = monthly_forecast.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📅 Monthly Summary",
        data=csv_monthly,
        file_name=f"monthly_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

with col_dl3:
    # Scenario comparison
    csv_scenarios = scenarios_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="🎯 All Scenarios",
        data=csv_scenarios,
        file_name=f"forecast_scenarios_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

# Footer
st.markdown("---")
st.caption(f"🔮 Forecast generated using AI models | Confidence Level: {confidence_level}% | Scenario: {growth_scenario}")