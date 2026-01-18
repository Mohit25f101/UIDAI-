import pandas as pd
import numpy as np
import osgit 
import random
from datetime import datetime, timedelta

# Setup
states = ["Uttar Pradesh", "Maharashtra", "Bihar", "West Bengal", "Madhya Pradesh", "Tamil Nadu", "Rajasthan", "Karnataka", "Gujarat", "Andhra Pradesh"]
districts = ["District_A", "District_B", "District_C", "District_D", "District_E"]
start_date = datetime(2023, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(365)]

data = []

for date in dates:
    for state in states:
        # --- NORMAL DATA ---
        enrolments = np.random.randint(100, 5000)
        updates = np.random.randint(50, 2000)
        
        # --- ANOMALY INJECTION (Masala) 🌶️ ---
        # 2% chance ki koi fraud hoga (Boht zyada Enrolments ya Updates)
        is_anomaly = False
        if random.random() < 0.02: 
            enrolments = np.random.randint(15000, 25000) # Achanak bohot saare log!
            is_anomaly = True
        
        # Updates anomaly (Fraud activity)
        if random.random() < 0.02:
            updates = np.random.randint(10000, 15000) # Achanak bohot updates!
            is_anomaly = True

        # Forecast column (Future prediction simulation)
        forecast = enrolments * np.random.uniform(0.9, 1.1)

        data.append([date, state, random.choice(districts), enrolments, updates, forecast, is_anomaly])

df = pd.DataFrame(data, columns=["Date", "State", "District", "Enrolments", "Updates", "Forecast", "Is_Anomaly"])
df.to_csv("data/processed_data.csv", index=False)
print("✅ Masaledaar Data Generated with Anomalies!")

# --- STEP 1: FOLDER SETUP ---
# Agar 'data' folder nahi mila to error aayega, isliye pehle hi bana lete hain
if not os.path.exists('data'):
    os.makedirs('data')

# --- STEP 2: SETTINGS ---
# In districts ka data show karenge dashboard par
districts = ['Lucknow', 'Varanasi', 'Kanpur Nagar', 'Agra', 'Meerut', 'Ghaziabad', 'Prayagraj']
# 2025 se start kar rahe hain taaki naya lage
start_date = datetime(2025, 1, 1)
total_days = 365 

data_list = []

print("Fake data generate ho raha hai... 2 min ruk.")

# --- STEP 3: MAIN LOGIC (LOOP) ---
for dist in districts:
    for i in range(total_days):
        # Aaj ki date nikal rahe hain
        current_date = start_date + timedelta(days=i)
        
        # WEEKEND LOGIC: 
        # Saturday (5) aur Sunday (6) ko enrolment kam hota hai naturally
        if current_date.weekday() >= 5:
            enrolment = np.random.randint(20, 100) # Weekend pe low traffic
        else:
            enrolment = np.random.randint(150, 600) # Working days pe heavy rush
            
        # Updates hamesha naye banwane walo se zyada hi hote hain (Common sense)
        updates = int(enrolment * np.random.uniform(1.2, 2.5))
        
        # PROBLEM CREATION:
        # Ye do districts mein intentionally kam number daal rahe hain
        # Taaki Map par 'Red' alert dikha sakein (Presentation ke liye)
        if dist in ['Bahraich', 'Shravasti']: 
            child_percent = np.random.uniform(0.05, 0.15) # Sirf 5-15% bache (Ye problem hai)
        else:
            child_percent = np.random.uniform(0.15, 0.35) # Baaki jagah sab sahi hai
            
        child_count = int(enrolment * child_percent)
        
        # FRAUD DETECTION (Member 2 wala part):
        # 100 mein se 1 case fraud/anomaly ho sakta hai
        if np.random.random() < 0.01:
            anomaly_status = 'Yes'
        else:
            anomaly_status = 'No'
        
        # FORECAST (Member 3 wala part):
        # Agle mahine ka prediction thoda bada ke likh dete hain
        future_demand = int(enrolment * 1.10)

        # Sab kuch list mein daal do
        data_list.append([
            current_date, 
            'Uttar Pradesh', 
            dist, 
            enrolment, 
            updates, 
            child_count, 
            anomaly_status, 
            future_demand
        ])

# --- STEP 4: SAVING ---
# Column names wahi rakhe hain jo dashboard mein use honge
cols = [
    'Date', 'State', 'District', 'Enrolments', 
    'Updates', 'Child_Enrolments', 'Is_Anomaly', 'Forecast'
]

df = pd.DataFrame(data_list, columns=cols)

# CSV file bana ke save kar rahe hain
file_path = 'data/processed_data.csv'
df.to_csv(file_path, index=False)

print(f"Done Save File!  {file_path}")
print(f"Total {len(df)} rows ban gayi hain.")