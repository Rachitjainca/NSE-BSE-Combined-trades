import os
import requests
import pandas as pd
import json
from datetime import datetime
import time
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIGURATION
API_URL = "https://client-pixel.groww.in/api/v1/ir-data/calculate"
# Save output in the same folder as this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = SCRIPT_DIR
TIMEOUT = 30

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
        
        # Make request (try GET first, can change to POST if needed)
        response = requests.get(API_URL, params=params, headers=headers, timeout=TIMEOUT, verify=False)
        response.raise_for_status()
        
        data = response.json()
        print("✓ Data fetched successfully!")
        
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching data: {e}")
        return None

def save_response(data, format_type='json'):
    """
    Append API response to a single file
    
    Args:
        data (dict): Data to save
        format_type (str): 'json' or 'csv'
    """
    if data is None:
        print("No data to save.")
        return
    
    if format_type == 'json':
        filepath = os.path.join(OUTPUT_DIR, "groww_ir_data.jsonl")
        try:
            # Append as JSONL (JSON Lines) format - one JSON object per line
            record = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            with open(filepath, 'a', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False)
                f.write('\n')
            print(f"✓ Data appended to {filepath}")
        except Exception as e:
            print(f"Error appending JSON: {e}")
    
    elif format_type == 'csv':
        filepath = os.path.join(OUTPUT_DIR, "groww_ir_data.csv")
        try:
            # Flatten the data for CSV output
            records = []
            if isinstance(data, dict) and 'data' in data:
                # Extract all metric types and their values
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
                # Check if file exists to determine if we should write header
                file_exists = os.path.exists(filepath)
                df.to_csv(filepath, mode='a', header=not file_exists, index=False)
                print(f"✓ Data appended to {filepath} ({len(records)} records)")
            else:
                print("No records to save.")
        except Exception as e:
            print(f"Error appending CSV: {e}")

def main():
    """Main execution function"""
    print("=" * 50)
    print("Groww IR Data Fetcher (Append Mode)")
    print("=" * 50)
    
    # Check if running in GitHub Actions
    in_github_actions = os.environ.get('GITHUB_ACTIONS', 'false').lower() == 'true'
    if in_github_actions:
        print("Running in GitHub Actions environment")
        print(f"Repository: {os.environ.get('GITHUB_REPOSITORY', 'N/A')}")
    
    # Uncomment below to add parameters if needed
    # params = {
    #     'param1': 'value1',
    #     'param2': 'value2'
    # }
    
    # Fetch data
    data = fetch_groww_data(params=None)
    
    if data:
        # Append to single files
        save_response(data, format_type='json')
        save_response(data, format_type='csv')
        
        # Also print data summary
        print("\nData summary:")
        if isinstance(data, dict):
            print(f"  Types count: {data.get('types_count', 'N/A')}")
            print(f"  Values per type: {data.get('values_per_type', 'N/A')}")
            print(f"  Metric types: {list(data.get('data', {}).keys())}")
            print(f"  Total records appended: {data.get('values_per_type', 0) * data.get('types_count', 0)}")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
