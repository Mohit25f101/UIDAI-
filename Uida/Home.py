# Final update
import streamlit as st
import os
import pandas as pd

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION (Ye sabse pehli line honi chahiye)
# ---------------------------------------------------------
st.set_page_config(page_title="UIDAI Dashboard", page_icon="🇮🇳", layout="wide")

# ---------------------------------------------------------
# 2. PATH FINDER LOGIC (The "GPS" Fix) 🛰️
# ---------------------------------------------------------
# Ye pata lagata hai ki Home.py exactly kahan rakha hai
current_dir = os.path.dirname(os.path.abspath(__file__))

# Phir wahan se rasta banata hai data aur logo tak
file_path = os.path.join(current_dir, "data", "processed_data.csv")
logo_path = os.path.join(current_dir, "assets", "uidai_logo.png")

# ---------------------------------------------------------
# 3. SIDEBAR & LOGO
# ---------------------------------------------------------
# Agar logo file milti hai, tabhi lagayenge
if os.path.exists(logo_path):
    st.logo(logo_path)
else:
    # Agar logo nahi mila toh console me bata dega (Code crash nahi hoga)
    print(f"Logo file not found at: {logo_path}")

st.sidebar.title("Navigation")

# Dropdown menu (Filter)
state_filter = st.sidebar.selectbox("State Select Kar:", ["All India", "Delhi", "Maharashtra", "UP"])
st.sidebar.divider()
st.sidebar.info("Data real-time update ho raha hai (Dummy mode).")

# ---------------------------------------------------------
# 4. MAIN DASHBOARD UI
# ---------------------------------------------------------
st.title("🇮🇳 Aadhaar Enrolment Intelligence System")

# Warning message (Prototype ke liye)
st.warning("⚠️ **Prototype Version:** This dashboard is running on **Synthetic Data** for demonstration.")

try:
    # --- DATA LOADING (Ab Absolute Path use kar rahe hain) ---
    df = pd.read_csv(file_path)
    
    # --- SECTION A: Key Metrics ---
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    # Safe logic: Agar column nahi mila toh 0 dikhayega (Crash nahi karega)
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
            st.error("⚠️ Data mein 'State' ya 'Enrolments' column nahi mila.")
        
    with col_chart2:
        st.markdown("### Update Trends")
        if 'Updates' in df.columns:
            st.line_chart(df, y="Updates")
        else:
            st.error("⚠️ Data mein 'Updates' column nahi mila.")

    # --- SECTION C: Raw Data ---
    with st.expander("Pura Data Table Dekhna Hai Toh Click Kar"):
        st.dataframe(df, use_container_width=True)
    
except FileNotFoundError:
    # Ab error aayega toh exact rasta batayega ki kahan dhoond raha tha
    st.error(f"🚨 Arre file nahi mili! Code is raste par dhoond raha tha: {file_path}")
    st.info("Ensure karo ki 'data' folder 'Uida' folder ke andar hi hai.")

except Exception as e:
    # Generic error catcher
    st.error(f"Kuch toh gadbad hai code me: {e}")