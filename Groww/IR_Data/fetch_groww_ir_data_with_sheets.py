import os
import requests
import pandas as pd
import json
from datetime import datetime, timezone
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
PREVIOUS_VALUES_FILE = os.path.join(OUTPUT_DIR, '.previous_metric_values.json')

# Google Sheets Configuration
GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID')
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, 'google_sheets_creds.json')

# Check if running in GitHub Actions environment
IN_GITHUB_ACTIONS = os.environ.get('GITHUB_ACTIONS', 'false').lower() == 'true'

def load_previous_metric_values():
    """Load previous metric values from file for change detection"""
    if os.path.exists(PREVIOUS_VALUES_FILE):
        try:
            with open(PREVIOUS_VALUES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            return {}
    return {}

def save_previous_metric_values(values_dict):
    """Save current metric values to file for next comparison"""
    try:
        with open(PREVIOUS_VALUES_FILE, 'w') as f:
            json.dump(values_dict, f, indent=2)
    except Exception:
        pass

def get_metric_value_key(metric_type, epoch_timestamp):
    """Create unique key for tracking metric values"""
    return f"{metric_type}_{epoch_timestamp}"

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
    Convert epoch time in milliseconds to DD/MM/YYYY HH:MM:SS GMT format
    
    Args:
        epoch_ms (int): Epoch time in milliseconds
    
    Returns:
        str: Formatted datetime string in GMT
    """
    try:
        epoch_seconds = epoch_ms / 1000
        dt = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc)
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError, OSError):
        return "N/A"

def convert_to_crores(value, metric_type):
    """
    Convert value to Crores (divide by 10^7) except for CNTU
    
    Args:
        value: Value to convert
        metric_type (str): Type of metric (CNTU keeps original value)
    
    Returns:
        float: Converted value or original if CNTU
    """
    if metric_type == 'CNTU' or value is None:
        return value
    
    try:
        return float(value) / 1e7
    except (ValueError, TypeError):
        return value

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
        print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S GMT')}")
        
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
        fetch_time_gmt = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
        
        if isinstance(data, dict) and 'data' in data:
            for metric_type, values in data['data'].items():
                for value_obj in values:
                    epoch_timestamp = value_obj.get('timestamp')
                    record = {
                        'fetch_time': fetch_time_gmt,
                        'metric_type': metric_type,
                        'epoch_timestamp': epoch_timestamp,
                        'value': convert_to_crores(value_obj.get('value'), metric_type)
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
    - All Data sheet: Always saves all records (historical)
    - Metric sheets: Only saves when values change (deduplication)
    
    Args:
        data (dict): Data to save
        client: gspread client
    """
    if data is None:
        return
    
    # Load previous values for change detection (always, even without client)
    previous_values = load_previous_metric_values()
    current_values = {}
    metric_records = {}
    
    # Prepare metric data for deduplication
    if isinstance(data, dict) and 'data' in data:
        for metric_type, values in data['data'].items():
            metric_records[metric_type] = []
            
            for value_obj in values:
                epoch_timestamp = value_obj.get('timestamp')
                raw_value = value_obj.get('value')
                converted_value = convert_to_crores(raw_value, metric_type)
                
                # Create key for tracking
                value_key = get_metric_value_key(metric_type, epoch_timestamp)
                current_values[value_key] = raw_value
                
                # Metric sheet: Only collect if value changed
                previous_value = previous_values.get(value_key)
                if previous_value is None or previous_value != raw_value:
                    metric_record = [
                        metric_type,
                        epoch_timestamp,
                        converted_value
                    ]
                    metric_records[metric_type].append(metric_record)
    
    # Save tracking file (always, for next comparison)
    save_previous_metric_values(current_values)
    
    # If no client, we can't save to Google Sheets
    if client is None:
        return
    
    try:
        # Open the spreadsheet
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        
        # Prepare data
        fetch_time_gmt = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
        all_records = []
        
        if isinstance(data, dict) and 'data' in data:
            for metric_type, values in data['data'].items():
                for value_obj in values:
                    epoch_timestamp = value_obj.get('timestamp')
                    converted_value = convert_to_crores(value_obj.get('value'), metric_type)
                    
                    # All Data sheet: Always append (historical record)
                    all_data_record = [
                        fetch_time_gmt,
                        metric_type,
                        epoch_timestamp,
                        converted_value
                    ]
                    all_records.append(all_data_record)
        
        # Update "All Data" sheet (always)
        try:
            all_data_sheet = spreadsheet.worksheet("All Data")
        except gspread.exceptions.WorksheetNotFound:
            all_data_sheet = spreadsheet.add_worksheet(title="All Data", rows=1000, cols=4)
            all_data_sheet.append_row([
                'Fetch Time', 'Metric Type', 'Epoch Timestamp', 'Value'
            ])
        
        if all_records:
            all_data_sheet.append_rows(all_records)
            print(f"✓ Google Sheets (All Data): {len(all_records)} records appended")
        
        # Update metric-specific sheets (only changed values)
        changed_count = 0
        for metric_type, records in metric_records.items():
            if records:  # Only update if there are changed values
                sheet_name = f"{metric_type}_Data"
                
                try:
                    metric_sheet = spreadsheet.worksheet(sheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    metric_sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=3)
                    metric_sheet.append_row([
                        'Metric Type', 'Epoch Timestamp', 'Value'
                    ])
                
                metric_sheet.append_rows(records)
                changed_count += len(records)
        
        if changed_count > 0:
            print(f"✓ Google Sheets: {changed_count} changed metric values saved")
        else:
            print("✓ Google Sheets: No metric values changed (deduplication)")
    
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
