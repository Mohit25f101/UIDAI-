import pandas as pd
import numpy as np
import os
import glob

# --- 1. AUTO-FIND THE FILE ---
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"📍 Scanning folder: {current_dir}")

# Look for specific likely filenames
potential_files = [
    "UIDAI_dashboard_master.csv",
    "raw_data.csv.csv",  # The common mistake
    "raw_data.csv",
    "aadhaar_monthly_district_UIDAI_READY.csv"
]

found_file = None

# Check specific names first
for f in potential_files:
    if os.path.exists(os.path.join(current_dir, f)):
        found_file = f
        break

# If not found, grab ANY csv file in the folder
if not found_file:
    csv_files = [f for f in os.listdir(current_dir) if f.endswith('.csv') and "processed_data" not in f]
    if csv_files:
        found_file = csv_files[0] # Take the first one found

if not found_file:
    print("\n❌ CRITICAL ERROR: No CSV file found in this folder!")
    print("👉 Please put 'UIDAI_dashboard_master.csv' inside D:\\UIDAI\\Uida\\")
    print(f"👉 Current files in folder: {os.listdir(current_dir)}")
    exit()

print(f"✅ Found file: {found_file}")

# --- 2. RENAME TO STANDARDIZE ---
raw_file_path = os.path.join(current_dir, "raw_data.csv")
found_file_path = os.path.join(current_dir, found_file)

# Only rename if it's not already named correctly
if found_file != "raw_data.csv":
    try:
        if os.path.exists(raw_file_path):
            os.remove(raw_file_path) # clear old one
        os.rename(found_file_path, raw_file_path)
        print(f"🔧 Automatically renamed '{found_file}' to 'raw_data.csv'")
    except Exception as e:
        print(f"⚠️ Could not rename file. Reading original name directly. ({e})")
        raw_file_path = found_file_path

# --- 3. PROCESS THE DATA ---
output_path = os.path.join(current_dir, "data", "processed_data.csv")

try:
    df = pd.read_csv(raw_file_path)
    print(f"📊 Processing {len(df)} rows...")

    # COLUMN MAPPING (Master -> Dashboard)
    column_mapping = {
        "state": "State",
        "district": "District",
        "latest_month": "Date",        
        "Risk_Tier": "Risk Level",     
        "MEGR_latest": "MEGR (%)",     
        "UPI_flag_latest": "Underperformance Flag",
        "ARS_latest": "Anomaly Score",
        "EVI_latest": "Volatility Score"
    }
    df = df.rename(columns=column_mapping)

    # FIXES
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Latest Month'] = df['Date'].dt.strftime('%b %Y')

    if 'Risk Level' in df.columns:
        df['Risk Level'] = df['Risk Level'].str.replace(' Risk', '', regex=False).str.strip()
    
    if 'Volatility Score' in df.columns:
        df['Volatility Level'] = np.where(df['Volatility Score'] > 0.5, 'High', 'Stable')

    # FILL MISSING VOLUME FOR CHARTS
    if 'Enrolments' not in df.columns:
        print("⚠️ Adding placeholder volume data for charts...")
        df['Enrolments'] = 1000 
        df['Updates'] = 200

    # SAVE
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print("-" * 30)
    print(f"🚀 SUCCESS! Data is ready.")
    print("-" * 30)

except Exception as e:
    print(f"❌ Processing Error: {e}")