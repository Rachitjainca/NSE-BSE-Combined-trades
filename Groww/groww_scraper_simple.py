import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_groww_simple():
    """
    Scrape Groww investor relations page using requests and BeautifulSoup
    """
    url = "https://groww.in/investor-relations"
    
    print(f"Fetching: {url}")
    print("=" * 50)
    
    try:
        # Fetch the page with headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://groww.in/',
        }
        
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
        
        print(f"✓ Page fetched successfully (Status: {response.status_code})")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find spans that might contain transacting users
        print("\nSearching for 'Total transacting Users' in page...")
        
        # Method 1: Search for text containing 'transacting'
        transacting_text = None
        for elem in soup.find_all(['span', 'div', 'p', 'h1', 'h2', 'h3']):
            text = elem.get_text(strip=True)
            if 'transacting' in text.lower() or 'users' in text.lower():
                print(f"Found: {text}")
                # If this element contains 'transacting', try to get the number from siblings
                parent = elem.parent
                if parent:
                    for sibling in parent.find_all(['span', 'div']):
                        text = sibling.get_text(strip=True)
                        # Look for numbers with commas or decimals
                        if re.search(r'\d+[\.\d,]*\d+', text):
                            transacting_text = text
                            print(f"  Found number: {text}")
        
        # Method 2: Look for large numbers in the page (likely stats)
        if not transacting_text:
            print("\nSearching for large numbers that might be user counts...")
            for elem in soup.find_all(['span']):
                text = elem.get_text(strip=True)
                # Look for numbers like 1.2M or 1,234,567
                if re.match(r'^\d+[\.,\dMKB\+]*$', text) and len(text) > 3:
                    print(f"Found number: {text}")
                    transacting_text = text
        
        # Method 3: Look for JSON data in script tags
        if not transacting_text:
            print("\nSearching in JavaScript data...")
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('transacting' in script.string.lower() or 'users' in script.string.lower()):
                    # Extract relevant part
                    script_text = script.string[:500]
                    print(f"Found in script: {script_text[:200]}")
        
        if transacting_text:
            print(f"\n{'='*50}")
            print(f"✅ Total transacting Users: {transacting_text}")
            print(f"{'='*50}\n")
            
            # Save to CSV
            timestamp = datetime.now()
            result_df = pd.DataFrame({
                'Date': [timestamp],
                'Total_Transacting_Users': [transacting_text],
                'Timestamp': [timestamp.isoformat()]
            })
            
            csv_path = "groww_user_data.csv"
            
            # Append to existing or create new
            try:
                existing_df = pd.read_csv(csv_path)
                result_df = pd.concat([existing_df, result_df], ignore_index=True)
            except FileNotFoundError:
                pass
            
            result_df.to_csv(csv_path, index=False)
            print(f"✓ Data saved to: {csv_path}")
            print(f"Total records: {len(result_df)}")
            
            return transacting_text
        else:
            print("❌ Could not find Total transacting Users in the page")
            print("\nPage structure sample (first 3000 chars):")
            print(response.text[:3000])
            return None
            
    except Exception as e:
        print(f"❌ Error occurred: {type(e).__name__}: {e}")
        return None

if __name__ == "__main__":
    scrape_groww_simple()
