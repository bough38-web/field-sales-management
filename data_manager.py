import pandas as pd
import os
import random
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

DB_FILE = "contracts_db.csv"

def init_db():
    if not os.path.exists(DB_FILE):
        try:
            print("Importing real data from Excel...")
            # Load real Excel data
            excel_path = '/Users/heebonpark/Downloads/정0224.xlsx'
            raw_df = pd.read_excel(excel_path)
            
            # Map columns to application schema
            # Required: Branch, Contract No, Company Name, Monthly Fee, Manager, Contact, Address, Latitude, Longitude, Status, Checked
            df = pd.DataFrame()
            df['Branch'] = raw_df['지사']
            df['Contract No'] = raw_df['계약번호']
            df['Company Name'] = raw_df['상호']
            df['Monthly Fee'] = raw_df[' 월정료(VAT미포함) ']
            df['Manager'] = raw_df['구역담당영업사원']
            df['Contact'] = raw_df['휴대폰']
            df['Address'] = raw_df['설치주소']
            
            # New columns based on request
            df['Stop Reason'] = raw_df['정지사유']
            df['Stop Start Date'] = pd.to_datetime(raw_df['정지시작일자'], errors='coerce').dt.strftime('%Y-%m-%d')
            df['Stop Days'] = raw_df['당월말_정지일수']
            
            # Additional columns
            df['Latitude'] = None
            df['Longitude'] = None
            df['Status'] = '미확인'
            df['Checked'] = False
            
            # Clean up potential NaNs
            df['Manager'] = df['Manager'].fillna('미배정')
            df['Address'] = df['Address'].fillna('주소없음')
            df['Contact'] = df['Contact'].fillna('연락처없음')
            df['Stop Reason'] = df['Stop Reason'].fillna('정상')
            df['Stop Start Date'] = df['Stop Start Date'].fillna('-')
            df['Stop Days'] = df['Stop Days'].fillna(0)
            df['Monthly Fee'] = pd.to_numeric(df['Monthly Fee'], errors='coerce').fillna(0)
            
            df.to_csv(DB_FILE, index=False)
            print(f"Successfully imported {len(df)} records into {DB_FILE}")
        except Exception as e:
            print(f"Error importing Excel: {e}")
            # Fallback mock data if excel fails or doesn't exist
            data = {
                "Branch": ["Seoul"],
                "Contract No": ["ERROR_001"],
                "Company Name": ["엑셀 로드 실패"],
                "Monthly Fee": [0],
                "Manager": ["Alice"],
                "Contact": ["010-0000-0000"],
                "Address": ["Seoul City Hall"],
                "Stop Reason": ["-"],
                "Stop Start Date": ["-"],
                "Stop Days": [0],
                "Latitude": [37.5665],
                "Longitude": [126.9780],
                "Status": ["미확인"],
                "Checked": [False]
            }
            pd.DataFrame(data).to_csv(DB_FILE, index=False)

import streamlit as st

@st.cache_data(ttl=3600)
def get_cached_data():
    df = pd.read_csv(DB_FILE)
    geolocator = Nominatim(user_agent="field_sales_app")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    missing_mask = df['Latitude'].isna() | df['Longitude'].isna()
    if missing_mask.any():
        for idx, row in df[missing_mask].iterrows():
            location = geocode(row['Address'])
            if location:
                df.at[idx, 'Latitude'] = location.latitude
                df.at[idx, 'Longitude'] = location.longitude
        df.to_csv(DB_FILE, index=False)
    
    return df

def get_data(query_filters=None):
    df = get_cached_data()
    if query_filters:
        for key, value in query_filters.items():
            df = df[df[key] == value]
    return df

def update_status(contract_no, new_status):
    df = pd.read_csv(DB_FILE)
    df.loc[df['Contract No'] == contract_no, 'Status'] = new_status
    df.to_csv(DB_FILE, index=False)
    get_cached_data.clear() # Clear cache on update

def update_checked(contract_no, is_checked):
    df = pd.read_csv(DB_FILE)
    df.loc[df['Contract No'] == contract_no, 'Checked'] = is_checked
    df.to_csv(DB_FILE, index=False)
    get_cached_data.clear() # Clear cache on update

def geocode_missing():
    pass

if __name__ == "__main__":
    init_db()

