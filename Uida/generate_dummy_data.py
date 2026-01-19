import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# --- PATH CONFIGURATION ---
current_dir = os.path.dirname(os.path.abspath(__file__))

# Universal Path Logic
if os.path.exists(os.path.join(current_dir, "data")):
    file_path = os.path.join(current_dir, "data", "processed_data.csv")
elif os.path.exists(os.path.join(current_dir, "Uida", "data")):
    file_path = os.path.join(current_dir, "Uida", "data", "processed_data.csv")
else:
    data_dir = os.path.join(current_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, "processed_data.csv")

print(f"📍 Data will be saved at: {file_path}")

# --- CONFIGURATION ---
states = ["Uttar Pradesh", "Maharashtra", "Bihar", "West Bengal", "Madhya Pradesh", "Tamil Nadu", "Rajasthan", "Karnataka", "Gujarat", "Andhra Pradesh"]
districts_map = {
    "Uttar Pradesh": ["Lucknow", "Varanasi", "Kanpur"],
    "Maharashtra": ["Pune", "Nagpur", "Mumbai"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur"],
    "West Bengal": ["Kolkata", "Howrah", "Darjeeling"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
    "Rajasthan": ["Jaipur", "Udaipur", "Kota"],
    "Karnataka": ["Bengaluru", "Mysuru", "Hubli"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
    "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur"]
}

start_date = datetime(2025, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(30)] 

data = []

print("🚀 Generating Strategic Dummy Data (with Latest Month)...")

for date in dates:
    for state in states:
        districts = districts_map.get(state, ["Generic District"])
        for district in districts:
            # --- RAW DATA ---
            enrolments = np.random.randint(100, 5000)
            updates = np.random.randint(50, 2000)
            is_anomaly = random.random() < 0.05 
            forecast = int(enrolments * 1.1)

            # --- STRATEGIC COLUMNS ---
            # 1. Latest Month (NEW COLUMN)
            latest_month = date.strftime("%b %Y") # e.g., "Jan 2025"

            # 2. MEGR (%) 
            megr = round(np.random.uniform(-10.0, 50.0), 2)
            
            # 3. Risk Level
            risk_level = np.random.choice(["Low", "Medium", "High"], p=[0.6, 0.3, 0.1])
            
            # 4. Volatility Level
            volatility = np.random.choice(["Stable", "Moderate", "High"], p=[0.7, 0.2, 0.1])
            
            # 5. Underperformance Flag
            underperf_flag = "Yes" if megr < 0 else "No"

            data.append([
                date, state, district, enrolments, updates, forecast, is_anomaly,
                latest_month, megr, risk_level, volatility, underperf_flag
            ])

# Create DataFrame with ALL columns
df = pd.DataFrame(data, columns=[
    "Date", "State", "District", "Enrolments", "Updates", "Forecast", "Is_Anomaly",
    "Latest Month", "MEGR (%)", "Risk Level", "Volatility Level", "Underperformance Flag"
])

# Boolean Fix
df["Is_Anomaly"] = df["Is_Anomaly"].astype(bool)

# Save
try:
    df.to_csv(file_path, index=False)
    print(f"✅ Success! Data saved with 'Latest Month' column.")
except Exception as e:
    print(f"❌ Error Saving File: {e}")