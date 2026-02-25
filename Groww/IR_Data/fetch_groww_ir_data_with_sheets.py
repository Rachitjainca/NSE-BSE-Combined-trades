import os
import requests
import pandas as pd
import json
from datetime import datetime
import time
import urllib3
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIGURATION
API_URL = "https://client-pixel.groww.in/api/v1/ir-data/calculate"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = SCRIPT_DIR
TIMEOUT = 30

# Google Sheets Configuration
GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID')
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, 'google_sheets_creds.json')

# Check if running in GitHub Actions environment
IN_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS', 'false').lower() == 'true'

def get_google_sheets_client():
    """
    Create and return Google Sheets API client
    
    Returns:
        gspread.Spreadsheet: Google Sheets client or None if not configured
    """
    try:
        if IN_GITHUB_ACTIONS:
            # Running in GitHub Actions - use credentials from environment variable
            credentials_json = os.environ.get('GOOGLE_SHEETS_CREDENTIALS')
            if not credentials_json:
                print("⚠️  GOOGLE_SHEETS_CREDENTIALS not set in GitHub Secrets")
                return None
            
            # Parse JSON string
            credentials_dict = json.loads(credentials_json)
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        else:
            # Running locally - use credentials file
            if not os.path.exists(CREDENTIALS_PATH):
                print("⚠️  Google Sheets credentials not found at:", CREDENTIALS_PATH)
                print("   Skipping Google Sheets integration")
                return None
            
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=scopes)
        
        client = gspread.authorize(creds)
        return client
    
    except Exception as e:
        print(f"⚠️  Error connecting to Google Sheets: {e}")
        return None

def epoch_to_formatted_time(epoch_ms):
    """
    Convert epoch time in milliseconds to DD/MM/YYYY HH:MM:SS format
    
    Args:
        epoch_ms (int): Epoch time in milliseconds
    
    Returns:
        str: Formatted datetime string
    """
    try:
        epoch_seconds = epoch_ms / 1000
        dt = datetime.fromtimestamp(epoch_seconds)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError, OSError):
        return "N/A"

# Create output directory if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_groww_data(params=None, headers=None):
    """
    Fetch data from Groww IR data API
    
    Args:
        params (dict): Query parameters for the API (optional)
        headers (dict): Custom headers (optional)
    
    Returns:
        dict: Response data from API
    """
    try:
        # Default headers
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        
        print(f"Fetching data from {API_URL}...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Make request
        response = requests.get(API_URL, params=params, headers=headers, timeout=TIMEOUT, verify=False)
        response.raise_for_status()
        
        data = response.json()
        print("✓ Data fetched successfully!")
        
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching data: {e}")
        return None

def save_to_csv(data):
    """
    Save API response to CSV file
    
    Args:
        data (dict): Data to save
    """
    if data is None:
        print("No data to save to CSV.")
        return
    
    filepath = os.path.join(OUTPUT_DIR, "groww_ir_data.csv")
    try:
        records = []
        if isinstance(data, dict) and 'data' in data:
            for metric_type, values in data['data'].items():
                for value_obj in values:
                    epoch_timestamp = value_obj.get('timestamp')
                    record = {
                        'fetch_time': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        'metric_type': metric_type,
                        'epoch_timestamp': epoch_timestamp,
                        'timestamp_readable': epoch_to_formatted_time(epoch_timestamp),
                        'value': value_obj.get('value')
                    }
                    records.append(record)
        
        if records:
            df = pd.DataFrame(records)
            file_exists = os.path.exists(filepath)
            df.to_csv(filepath, mode='a', header=not file_exists, index=False)
            print(f"✓ CSV: {len(records)} records appended")
        else:
            print("No records to save to CSV.")
    except Exception as e:
        print(f"Error appending CSV: {e}")

def save_to_google_sheets(data, client):
    """
    Save API response to Google Sheets
    Creates "All Data" sheet and individual metric type sheets
    
    Args:
        data (dict): Data to save
        client: gspread client
    """
    if data is None or client is None:
        return
    
    try:
        # Open the spreadsheet
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        
        # Prepare data
        fetch_time_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        all_records = []
        metric_records = {}
        
        if isinstance(data, dict) and 'data' in data:
            for metric_type, values in data['data'].items():
                metric_records[metric_type] = []
                
                for value_obj in values:
                    epoch_timestamp = value_obj.get('timestamp')
                    record = [
                        fetch_time_str,
                        metric_type,
                        epoch_timestamp,
                        epoch_to_formatted_time(epoch_timestamp),
                        value_obj.get('value')
                    ]
                    all_records.append(record)
                    metric_records[metric_type].append(record)
        
        # Update "All Data" sheet
        try:
            all_data_sheet = spreadsheet.worksheet("All Data")
        except gspread.exceptions.WorksheetNotFound:
            all_data_sheet = spreadsheet.add_worksheet(title="All Data", rows=1000, cols=5)
            # Add header
            all_data_sheet.append_row([
                'Fetch Time', 'Metric Type', 'Epoch Timestamp', 'Timestamp Readable', 'Value'
            ])
        
        if all_records:
            all_data_sheet.append_rows(all_records)
            print(f"✓ Google Sheets (All Data): {len(all_records)} records appended")
        
        # Update metric-specific sheets
        for metric_type, records in metric_records.items():
            sheet_name = f"{metric_type}_Data"
            
            try:
                metric_sheet = spreadsheet.worksheet(sheet_name)
            except gspread.exceptions.WorksheetNotFound:
                metric_sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=5)
                # Add header
                metric_sheet.append_row([
                    'Fetch Time', 'Metric Type', 'Epoch Timestamp', 'Timestamp Readable', 'Value'
                ])
            
            if records:
                metric_sheet.append_rows(records)
        
        print(f"✓ Google Sheets ({len(metric_records)} metric sheets): Updated")
    
    except gspread.exceptions.APIError as e:
        print(f"✗ Google Sheets API Error: {e}")
    except Exception as e:
        print(f"✗ Error updating Google Sheets: {e}")

def main():
    """Main execution function"""
    print("=" * 60)
    print("Groww IR Data Fetcher (CSV + Google Sheets)")
    print("=" * 60)
    
    if IN_GITHUB_ACTIONS:
        print("✓ Running in GitHub Actions environment")
        print(f"  Repository: {os.environ.get('GITHUB_REPOSITORY', 'N/A')}")
    else:
        print("✓ Running locally")
    
    # Fetch data
    data = fetch_groww_data(params=None)
    
    if data:
        # Save to CSV
        save_to_csv(data)
        
        # Save to Google Sheets
        sheets_client = get_google_sheets_client()
        if sheets_client and GOOGLE_SHEET_ID:
            save_to_google_sheets(data, sheets_client)
        elif not IN_GITHUB_ACTIONS:
            print("⚠️  Google Sheets not configured")
        
        # Print data summary
        print("\n📊 Data summary:")
        if isinstance(data, dict):
            print(f"  Types count: {data.get('types_count', 'N/A')}")
            print(f"  Values per type: {data.get('values_per_type', 'N/A')}")
            print(f"  Metric types: {list(data.get('data', {}).keys())}")
            print(f"  Total records: {data.get('values_per_type', 0) * data.get('types_count', 0)}")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
