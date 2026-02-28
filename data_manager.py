import pandas as pd
import os
import random
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

DB_FILE = "contracts_db.csv"

def init_db():
    if not os.path.exists(DB_FILE):
        # Create mock data
        data = {
            "Branch": ["Seoul", "Seoul", "Busan", "Busan", "Daegu"],
            "Contract No": ["C001", "C002", "C003", "C004", "C005"],
            "Company Name": ["Alpha Tech", "Beta Corp", "Gamma Inc", "Delta LLC", "Epsilon Co"],
            "Monthly Fee": [100000, 150000, 120000, 200000, 90000],
            "Manager": ["Alice", "Alice", "Bob", "Bob", "Charlie"],
            "Contact": ["010-1111-2222", "010-3333-4444", "010-5555-6666", "010-7777-8888", "010-9999-0000"],
            "Address": ["Seoul City Hall", "Gangnam Station", "Busan Station", "Haeundae Beach", "Dongdaegu Station"],
            "Latitude": [37.5665, 37.4979, 35.1152, 35.1587, 35.8797],
            "Longitude": [126.9780, 127.0276, 129.0422, 129.1604, 128.6285],
            "Status": ["미확인", "진행중", "완료", "미확인", "진행중"],
            "Checked": [False, True, True, False, True]
        }
        df = pd.DataFrame(data)
        df.to_csv(DB_FILE, index=False)
        print(f"Initialized mock DB at {DB_FILE}")

def get_data(query_filters=None):
    df = pd.read_csv(DB_FILE)
    if query_filters:
        for key, value in query_filters.items():
            df = df[df[key] == value]
    return df

def update_status(contract_no, new_status):
    df = pd.read_csv(DB_FILE)
    df.loc[df['Contract No'] == contract_no, 'Status'] = new_status
    df.to_csv(DB_FILE, index=False)

def update_checked(contract_no, is_checked):
    df = pd.read_csv(DB_FILE)
    df.loc[df['Contract No'] == contract_no, 'Checked'] = is_checked
    df.to_csv(DB_FILE, index=False)

def geocode_missing():
    df = pd.read_csv(DB_FILE)
    geolocator = Nominatim(user_agent="field_sales_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    missing_mask = df['Latitude'].isna() | df['Longitude'].isna()
    if missing_mask.any():
        print("Geocoding missing coordinates...")
        for idx, row in df[missing_mask].iterrows():
            location = geocode(row['Address'])
            if location:
                df.at[idx, 'Latitude'] = location.latitude
                df.at[idx, 'Longitude'] = location.longitude
        df.to_csv(DB_FILE, index=False)
    
if __name__ == "__main__":
    init_db()
    geocode_missing()
