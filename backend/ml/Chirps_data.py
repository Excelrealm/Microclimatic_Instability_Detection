import os
import pandas as pd
import ee

print("==================================================")
print("   CHIRPS 10-YEAR DATA DOWNLOADER INITIALIZED     ")
print("==================================================")

# 1. Authenticate and Connect to Google Earth Engine
try:
    print("Checking cloud connection credentials...")
    ee.Initialize()
    print("Google Earth Engine Status: Connected successfully!")
except Exception:
    print("\nAction Required: Directing to Google Browser Authentication...")
    print("Please click the link generated below, log into your Google account,")
    print("and paste the verification code back into this terminal.")
    ee.Authenticate()
    ee.Initialize()

# 2. Pinpoint Coordinates for Covenant University, Ota, Nigeria
LATITUDE = 6.6725
LONGITUDE = 3.1537
poi = ee.Geometry.Point([LONGITUDE, LATITUDE])
print(f"\nTargeting Location: Covenant University Campus ({LATITUDE}, {LONGITUDE})")

# 3. Dynamic Absolute Paths matching your backend/ml/ layout
# This finds where Chirps_data.py is on your disk and paths back to backend/data/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "data"))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chirps_ota_daily.csv")

# Create the backend/data directory safely if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 4. Fetch the Global Cloud Archive for the 10-Year Span (2016 - 2025)
START_DATE = "2016-01-01"
END_DATE = "2025-12-31"
print(f"Slicing 10-year dataset stack ({START_DATE} to {END_DATE})...")

chirps_collection = (
    ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
    .filterDate(START_DATE, END_DATE)
    .select('precipitation')
)

# 5. Parallel Processing Engine running on Google's Cloud Infrastructure
print("Extracting precipitation grid arrays over the timeline simultaneously...")

def extract_point_data(image):
    stats = image.reduceRegion(
        reducer=ee.Reducer.first(),
        geometry=poi,
        scale=5000  # Resolution matching CHIRPS' ~5km satellite grid cells
    )
    return ee.Feature(None, {
        'date': image.date().format('YYYY-MM-DD'),
        'precipitation': stats.get('precipitation')
    })

# Gather data from the cloud array down into your local machine memory
extracted_features = chirps_collection.map(extract_point_data).getInfo()

# 6. Parse and Structure the Data Payload into an ML Training Dataset
print("Formatting incoming text arrays into local data structures...")
data_records = []

for feature in extracted_features.get('features', []):
    props = feature.get('properties', {})
    precip_val = props.get('precipitation')
    
    # Handle satellite data gap buffers or negative NoData flags gracefully
    if precip_val is None or precip_val < 0:
        precip_val = 0.0
        
    data_records.append({
        "date": props.get('date'),
        "precipitation": precip_val
    })

# Build, sort chronologically, and save the Dataframe to CSV
df = pd.DataFrame(data_records)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')
df.to_csv(OUTPUT_FILE, index=False)

print("\n==================================================")
print("             PROCESS RUN COMPLETE                 ")
print("==================================================")
print(f"SUCCESS: 10 Years of Data Saved to local workspace.")
print(f"File Destination: {OUTPUT_FILE}")
print(f"Total Records Extracted: {len(df)} days.")
print("\nSample of your generated ML training dataset:")
print(df.head(10))
print("==================================================")