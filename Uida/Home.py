import streamlit as st
import os
import pandas as pd

# Page ki setting (Sirf ek baar honi chahiye - Duplicate hataya)
st.set_page_config(page_title="UIDAI Dashboard", page_icon="🇮🇳", layout="wide")

# --- PATH FINDER LOGIC (GPS) ---
# Ye code pata lagayega ki Home.py kahan hai, aur wahan se data folder dhoondega
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "data", "processed_data.csv")
logo_path = os.path.join(current_dir, "assets", "uidai_logo.png")

# --- SIDEBAR ---
# Agar logo file exist karti hai tabhi dikhayega, warna error nahi dega
if os.path.exists(logo_path):
    st.logo(logo_path)

st.sidebar.title("Navigation")

# Dropdown menu add kar diya filter ke liye
state_filter = st.sidebar.selectbox("State Select Kar:", ["All India", "Delhi", "Maharashtra", "UP"])
st.sidebar.divider()
st.sidebar.info("Data real-time update ho raha hai (Dummy mode).")
# --- SIDEBAR END ---

# Main Title
st.title("🇮🇳 Aadhaar Enrolment Intelligence System")

# Disclaimer (Optional - jo humne pehle discuss kiya tha)
st.warning("⚠️ **Prototype Version:** This dashboard is running on **Synthetic Data** for demonstration.")

try:
    # Data utha raha hu (Ab Absolute Path se)
    df = pd.read_csv(file_path)
    
    # 1. Top Metrics Section
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    # Simple check taaki agar column name galat ho toh code phate nahi
    total_enrolments = df['Enrolments'].sum() if 'Enrolments' in df.columns else 0
    total_updates = df['Updates'].sum() if 'Updates' in df.columns else 0

    col1.metric("Total Enrolments", f"{total_enrolments:,}")
    col2.metric("Updates Pending", f"{total_updates:,}")
    col3.metric("Critical Alerts", "12", delta="-2", delta_color="inverse")
    
    st.divider() # Line kheech di beech me
    
    # 2. Charts Section (Visuals)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### State-wise Enrolments")
        if 'State' in df.columns and 'Enrolments' in df.columns:
            st.bar_chart(df, x="State", y="Enrolments", color="#ffaa00")
        else:
            st.error("CSV mein 'State' ya 'Enrolments' column nahi mila.")
        
    with col_chart2:
        st.markdown("### Update Trends")
        if 'Updates' in df.columns:
            st.line_chart(df, y="Updates")
        else:
            st.error("CSV mein 'Updates' column nahi mila.")

    # 3. Raw Data (Chupa ke rakha hai expander me)
    with st.expander("Pura Data Table Dekhna Hai Toh Click Kar"):
        st.dataframe(df, use_container_width=True)
    
except FileNotFoundError:
    st.error(f"🚨 Arre file nahi mili! Code is raste par dhoond raha tha: {file_path}")
    st.info("Ensure ki 'data' folder 'Uida' folder ke andar hi hai.")

except Exception as e:
    # Agar kuch aur phata toh ye error aayega
    st.error(f"Kuch toh gadbad hai code me: {e}")