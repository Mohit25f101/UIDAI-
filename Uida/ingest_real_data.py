import pandas as pd
import numpy as np
import os

# --- 1. SETUP PATHS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
raw_file = os.path.join(current_dir, "aadhaar_monthly_district_UIDAI_READY.csv")

# Universal Data Path
if os.path.exists(os.path.join(current_dir, "data")):
    output_path = os.path.join(current_dir, "data", "processed_data.csv")
else:
    os.makedirs(os.path.join(current_dir, "data"), exist_ok=True)
    output_path = os.path.join(current_dir, "data", "processed_data.csv")

print(f"📂 Reading Raw File: {raw_file}")

try:
    # --- 2. LOAD & CLEAN ---
    df = pd.read_csv(raw_file)
    
    # Column Mapping (Small -> Capital)
    df = df.rename(columns={
        "state": "State",
        "district": "District",
        "month": "Date",
        "total_enrolments": "Enrolments"
    })
    
    # Fix Date Format (YYYY-MM -> DateTime)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m')
    # Add 'Latest Month' text for Dashboard
    df['Latest Month'] = df['Date'].dt.strftime('%b %Y')

    print("✅ Columns Renamed & Date Fixed.")

    # --- 3. GENERATE MISSING METRICS ---
    # (Updates data missing hai, toh hum Enrolments ka 20-40% estimate karenge)
    np.random.seed(42) # Consistent results
    df['Updates'] = (df['Enrolments'] * np.random.uniform(0.2, 0.4, size=len(df))).astype(int)
    
    # (Forecast: Next month prediction = Current + Random Noise)
    df['Forecast'] = (df['Enrolments'] * np.random.uniform(0.9, 1.1, size=len(df))).astype(int)
    
    # (Anomaly: Agar Enrolments > 98th Percentile of District, mark True)
    threshold = df['Enrolments'].quantile(0.98)
    df['Is_Anomaly'] = df['Enrolments'] > threshold

    print("✅ Updates, Forecast & Anomalies Generated.")

    # --- 4. CALCULATE STRATEGIC SIGNALS (REAL MATHS) 🧠 ---
    # Sort by District and Date to calculate Growth (MEGR)
    df = df.sort_values(by=['State', 'District', 'Date'])
    
    # Calculate Previous Month Enrolment
    df['Prev_Enrolment'] = df.groupby(['State', 'District'])['Enrolments'].shift(1)
    
    # Calculate MEGR (%) = ((Current - Prev) / Prev) * 100
    df['MEGR (%)'] = ((df['Enrolments'] - df['Prev_Enrolment']) / df['Prev_Enrolment']) * 100
    df['MEGR (%)'] = df['MEGR (%)'].fillna(0).round(2) # Fill first month with 0

    # Risk Level Logic
    # High Risk if Growth is crazy high (>50%) or Drop is huge (<-30%)
    conditions = [
        (df['MEGR (%)'] > 50) | (df['MEGR (%)'] < -30), # High Risk
        (df['MEGR (%)'] > 20) | (df['MEGR (%)'] < -10)  # Medium Risk
    ]
    choices = ['High', 'Medium']
    df['Risk Level'] = np.select(conditions, choices, default='Low')

    # Volatility Level (Random for demo based on Risk)
    df['Volatility Level'] = np.where(df['Risk Level'] == 'High', 'High', 'Stable')

    # Underperformance Flag (If Growth is Negative)
    df['Underperformance Flag'] = np.where(df['MEGR (%)'] < 0, 'Yes', 'No')

    print("✅ Strategic Signals (MEGR, Flags, Risk) Calculated.")

    # --- 5. SAVE FINAL FILE ---
    # Select only latest month for Overview (Optional: Keep all for charts)
    # We keep FULL data for charts, Dashboard handles filtering.
    
    df.to_csv(output_path, index=False)
    print(f"🚀 SUCCESS! Processed data saved to: {output_path}")
    print("👉 Now run: 'streamlit run Overview.py'")

except Exception as e:
    print(f"❌ Error: {e}")