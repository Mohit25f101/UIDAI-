# Final update
import streamlit as st
import os
import pandas as pd

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION (Must be the first command)
# ---------------------------------------------------------
st.set_page_config(page_title="UIDAI Dashboard", page_icon="🇮🇳", layout="wide")

# ---------------------------------------------------------
# 2. PATH FINDER LOGIC (Universal Path Fix) 🛰️
# ---------------------------------------------------------
# Determine the absolute path of this script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct paths for data and assets based on script location
file_path = os.path.join(current_dir, "data", "processed_data.csv")
logo_path = os.path.join(current_dir, "assets", "uidai_logo.png")

# ---------------------------------------------------------
# 3. SIDEBAR & LOGO
# ---------------------------------------------------------
# Display logo only if the file exists
if os.path.exists(logo_path):
    st.logo(logo_path)
else:
    # Log to console if logo is missing (prevents crash)
    print(f"Logo file not found at: {logo_path}")

st.sidebar.title("Navigation")

# Dropdown menu (Filter)
state_filter = st.sidebar.selectbox("Select State:", ["All India", "Delhi", "Maharashtra", "UP"])
st.sidebar.divider()
st.sidebar.info("Real-time data simulation active.")

# ---------------------------------------------------------
# 4. MAIN DASHBOARD UI
# ---------------------------------------------------------
st.title("🇮🇳 Aadhaar Enrolment Intelligence System")

# Warning message (For Prototype)
st.warning("⚠️ **Prototype Version:** This dashboard is running on **Real Strategic Data** for demonstration.")

try:
    # --- DATA LOADING (Using Absolute Path) ---
    df = pd.read_csv(file_path)
    
    # =========================================================
    # 🆕 NEW FEATURE: AI EXECUTIVE SUMMARY & DOWNLOAD
    # =========================================================
    st.markdown("### 📢 AI System Insights")

    # 1. Calculate Logic for the Summary
    total_districts = len(df)
    
    # Check if Risk Level exists to generate insights
    if 'Risk Level' in df.columns:
        high_risk_count = len(df[df['Risk Level'] == 'High'])
        
        # Find the state with the most high-risk districts
        if 'State' in df.columns:
            risk_by_state = df[df['Risk Level'] == 'High']['State'].value_counts()
            
            if not risk_by_state.empty:
                top_risk_state = risk_by_state.idxmax()
                risk_count_state = risk_by_state.max()
                summary_text = (
                    f"**System Status:** Analyzing **{total_districts}** districts. "
                    f"Currently, **{high_risk_count} districts** are flagged as **High Risk**. "
                    f"⚠️ **Action Required:** The state of **{top_risk_state}** has the highest concentration "
                    f"of issues ({risk_count_state} districts)."
                )
                status_color = "error" # Red box
            else:
                summary_text = "✅ **System Status:** All districts are performing within stable parameters. No critical risks detected."
                status_color = "success" # Green box
        else:
            summary_text = f"**System Status:** Found {high_risk_count} High Risk districts."
            status_color = "warning"
    else:
        summary_text = "System is gathering data... (Risk Analysis pending)"
        status_color = "info"

    # 2. Display the Summary Box
    if status_color == "error":
        st.error(summary_text)
    elif status_color == "success":
        st.success(summary_text)
    else:
        st.info(summary_text)

    # 3. Add Download Button (The "Takeaway")
    col_d1, col_d2 = st.columns([3, 1])
    with col_d2:
        # Filter only the important rows (High Risk) if possible
        if 'Risk Level' in df.columns:
            report_df = df[df['Risk Level'] == 'High']
            csv = report_df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Risk Report",
                data=csv,
                file_name="High_Risk_Report_UIDAI.csv",
                mime="text/csv",
            )
    st.divider() # Line separator
    # =========================================================

    # --- SECTION A: Key Metrics ---
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    # Safe logic: Displays 0 if column is missing (prevents crash)
    total_enrolments = df['Enrolments'].sum() if 'Enrolments' in df.columns else 0
    total_updates = df['Updates'].sum() if 'Updates' in df.columns else 0
    
    # Calculate critical alerts dynamically if Risk Level exists
    if 'Risk Level' in df.columns:
        critical_alerts = len(df[df['Risk Level'] == 'High'])
    else:
        critical_alerts = 0

    col1.metric("Total Enrolments (Est.)", f"{total_enrolments:,}")
    col2.metric("Updates Pending (Est.)", f"{total_updates:,}")
    col3.metric("Critical Alerts", f"{critical_alerts}", delta="Live", delta_color="inverse")
    
    st.divider() # Line separator
    
    # --- SECTION B: Charts ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### State-wise Enrolments")
        if 'State' in df.columns and 'Enrolments' in df.columns:
            # Aggregate by State for cleaner chart
            state_data = df.groupby('State')['Enrolments'].sum().sort_values(ascending=False).head(10)
            st.bar_chart(state_data, color="#ffaa00") 
        else:
            st.error("⚠️ 'State' or 'Enrolments' column missing in data.")
        
    with col_chart2:
        st.markdown("### Update Trends")
        if 'Updates' in df.columns:
            st.line_chart(df['Updates'].head(50)) # Limit to 50 pts for clarity
        else:
            st.error("⚠️ 'Updates' column missing in data.")

    # --- SECTION C: Raw Data ---
    with st.expander("View Full Data Table"):
        st.dataframe(df, use_container_width=True)
    
except FileNotFoundError:
    # Detailed error message for debugging paths
    st.error(f"🚨 File not found! The code searched at: {file_path}")
    st.info("Please ensure the 'data' folder exists within the 'Uida' directory.")

except Exception as e:
    # Generic error catcher
    st.error(f"An error occurred: {e}")