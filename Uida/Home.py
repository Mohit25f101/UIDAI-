import streamlit as st
import pandas as pd

# Page ki setting
st.set_page_config(page_title="UIDAI Dashboard", page_icon="🇮🇳", layout="wide")

# --- SIDEBAR ---
st.set_page_config(page_title="UIDAI Dashboard", page_icon="🇮🇳", layout="wide")

# --- NEW MAGIC CODE (Logo ko sabse upar bhejne ke liye) ---
st.logo("assets/uidai_logo.png")
st.sidebar.title("Navigation")

# Dropdown menu add kar diya filter ke liye
state_filter = st.sidebar.selectbox("State Select Kar:", ["All India", "Delhi", "Maharashtra", "UP"])
st.sidebar.divider()
st.sidebar.info("Data real-time update ho raha hai (Dummy mode).")
# --- SIDEBAR END ---

# Main Title
st.title("🇮🇳 Aadhaar Enrolment Intelligence System")

try:
    # Data utha raha hu
    df = pd.read_csv('data/processed_data.csv')
    
    # 1. Top Metrics Section
    st.subheader("Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Total Enrolments", f"{df['Enrolments'].sum():,}")
    col2.metric("Updates Pending", f"{df['Updates'].sum():,}")
    col3.metric("Critical Alerts", "12", delta="-2", delta_color="inverse") # Delta dikhaya taaki fancy lage
    
    st.divider() # Line kheech di beech me
    
    # 2. Charts Section (Visuals)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### State-wise Enrolments")
        # Ye check kar lio ki csv me 'State' aur 'Enrolments' column ka naam same hai ya nahi
        st.bar_chart(df, x="State", y="Enrolments", color="#ffaa00") 
        
    with col_chart2:
        st.markdown("### Update Trends")
        # Line chart dikhane ke liye
        st.line_chart(df, y="Updates")

    # 3. Raw Data (Chupa ke rakha hai expander me)
    with st.expander("Pura Data Table Dekhna Hai Toh Click Kar"):
        st.dataframe(df, use_container_width=True)
    
except FileNotFoundError:
    st.error("Arre file nahi mili! 'processed_data.csv' check kar le folder me hai ya nahi.")
except Exception as e:
    # Agar kuch aur phata toh ye error aayega
    st.error(f"Kuch toh gadbad hai code me: {e}")