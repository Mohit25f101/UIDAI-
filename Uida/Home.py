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
st.warning("⚠️ **Prototype Version:** This dashboard is running on **Synthetic Data** for demonstration.")

try:
    # --- DATA LOADING (Using Absolute Path) ---
    df = pd.read_csv(file_path)
    
    # --- SECTION A: Key Metrics ---
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    # Safe logic: Displays 0 if column is missing (prevents crash)
    total_enrolments = df['Enrolments'].sum() if 'Enrolments' in df.columns else 0
    total_updates = df['Updates'].sum() if 'Updates' in df.columns else 0

    col1.metric("Total Enrolments", f"{total_enrolments:,}")
    col2.metric("Updates Pending", f"{total_updates:,}")
    col3.metric("Critical Alerts", "12", delta="-2", delta_color="inverse")
    
    st.divider() # Line separator
    
    # --- SECTION B: Charts ---
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### State-wise Enrolments")
        if 'State' in df.columns and 'Enrolments' in df.columns:
            st.bar_chart(df, x="State", y="Enrolments", color="#ffaa00") 
        else:
            st.error("⚠️ 'State' or 'Enrolments' column missing in data.")
        
    with col_chart2:
        st.markdown("### Update Trends")
        if 'Updates' in df.columns:
            st.line_chart(df, y="Updates")
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