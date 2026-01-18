import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# --- PATH SETTING (GPS) ---
# Script jahan hai wahan se 'data' folder dhoondo
current_dir = os.path.dirname(os.path.abspath(__file__))

# Agar script Uida folder ke andar hai, toh data folder wahin hoga
# Agar bahar hai, to Uida/data dhoondna padega. Hum safe khelte hain:
if os.path.exists(os.path.join(current_dir, "data")):
    file_path = os.path.join(current_dir, "data", "processed_data.csv")
elif os.path.exists(os.path.join(current_dir, "Uida", "data")):
    file_path = os.path.join(current_dir, "Uida", "data", "processed_data.csv")
else:
    # Agar folder hi nahi mila to bana lo
    data_dir = os.path.join(current_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, "processed_data.csv")

print(f"📍 Data yahan save hoga: {file_path}")

# --- CONFIGURATION ---
states = ["Uttar Pradesh", "Maharashtra", "Bihar", "West Bengal", "Madhya Pradesh", "Tamil Nadu", "Rajasthan", "Karnataka", "Gujarat", "Andhra Pradesh"]
districts = ["Lucknow", "Varanasi", "Pune", "Nagpur", "Patna", "Kolkata", "Jaipur", "Bengaluru", "Ahmedabad", "Chennai"]
start_date = datetime(2025, 1, 1) # Future date for freshness
dates = [start_date + timedelta(days=i) for i in range(365)]

data = []

print("🚀 Generating Masaledaar Data...")

for date in dates:
    for state in states:
        # --- NORMAL TRAFFIC ---
        enrolments = np.random.randint(100, 5000)
        updates = np.random.randint(50, 2000)
        
        # --- ANOMALY INJECTION (Fraud Logic) 🌶️ ---
        # Dashboard ko 'True' chahiye, 'Yes' nahi.
        is_anomaly = False 
        
        # Chance 1: Enrolment Spike (Fake IDs?)
        if random.random() < 0.03:  # 3% chance
            enrolments = np.random.randint(15000, 30000) # Huge spike
            is_anomaly = True
        
        # Chance 2: Update Spike (Correction Fraud?)
        if random.random() < 0.03: # 3% chance
            updates = np.random.randint(12000, 20000) # Huge spike
            is_anomaly = True

        # Forecast Logic
        forecast = int(enrolments * np.random.uniform(0.9, 1.1))

        data.append([date, state, random.choice(districts), enrolments, updates, forecast, is_anomaly])

# DataFrame Creation
df = pd.DataFrame(data, columns=["Date", "State", "District", "Enrolments", "Updates", "Forecast", "Is_Anomaly"])

# --- IMPORTANT: Boolean Convert ---
# Ensure karo ki column True/False hi ho (String nahi)
df["Is_Anomaly"] = df["Is_Anomaly"].astype(bool)

# Save
try:
    df.to_csv(file_path, index=False)
    print(f"✅ Success! Data saved with {len(df[df['Is_Anomaly']==True])} Anomalies.")
except Exception as e:
    print(f"❌ Error Saving File: {e}")