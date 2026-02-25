import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime
import re

async def scrape_groww_data():
    """
    Scrape Total transacting Users from Groww Investor Relations page using Playwright
    """
    url = "https://groww.in/investor-relations"
    
    print(f"Starting web scraper for: {url}")
    print("=" * 50)
    
    async with async_playwright() as p:
        try:
            # Launch browser
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            # Set larger viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            print(f"Loading page: {url}")
            # Wait for network to be idle to ensure all JS is executed
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            print(f"[OK] Page loaded: {url}")
            
            # Wait a bit more for dynamic content to load
            await page.wait_for_timeout(3000)
            
            # Try to find the element containing the total transacting users number
            # Looking for elements with specific text patterns
            print("\nWaiting for data to render...")
            
            # Get all text content from the page
            page_text = await page.locator('body').text_content()
            
            # Look for numbers that appear after "Total Transacting Users"
            # The data might be in a specific format like "1.2M" or "12,34,567"
            lines = page_text.split('\n')
            
            transacting_users = None
            for i, line in enumerate(lines):
                if 'Total Transacting Users' in line or 'total transacting users' in line.lower():
                    print(f"Found 'Total Transacting Users' near: {line.strip()[:100]}")
                    
                    # Check the next few lines for the number
                    for j in range(i, min(i+5, len(lines))):
                        next_line = lines[j].strip()
                        # Look for numbers with M, K, or digit patterns
                        numbers = re.findall(r'[\d,\.]+[MK]?(?:\+)?|[\d,]+', next_line)
                        for num in numbers:
                            if num and num not in ['30', '2025', '9', '30']:  # Exclude dates and common false positives
                                print(f"Found potential number: {num}")
                                if not transacting_users:
                                    transacting_users = num
            
            # Alternative: Try using XPath directly
            if not transacting_users:
                print("\nTrying XPath approach...")
                try:
                    xpath = '//span[contains(text(), "M") or contains(text(), "K")]'
                    elements = page.locator(xpath)
                    count = await elements.count()
                    print(f"Found {count} matching elements")
                    
                    for i in range(min(5, count)):
                        try:
                            text = await elements.nth(i).text_content()
                            print(f"Element {i}: {text}")
                            if re.search(r'\d+[\.,\dMK]+', text):
                                transacting_users = text.strip()
                                break
                        except:
                            pass
                except Exception as e:
                    print(f"XPath approach failed: {e}")
            
            # Last resort: get the entire page HTML and search
            if not transacting_users:
                print("\nSearching page HTML...")
                html = await page.content()
                # Look for the data in script tags or specific patterns
                matches = re.findall(r'>(\d+[.,\dMKB\+]*)<', html)
                for match in matches[:10]:
                    if len(match) > 2 and any(c in match for c in ['M', 'K', ',']):
                        print(f"Found in HTML: {match}")
                        if not transacting_users:
                            transacting_users = match
            
            if transacting_users:
                print(f"\n{'='*50}")
                print(f"✅ Total transacting Users: {transacting_users}")
                print(f"{'='*50}\n")
                
                # Save to CSV
                timestamp = datetime.now()
                result_df = pd.DataFrame({
                    'Date': [timestamp],
                    'Total_Transacting_Users': [transacting_users],
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
                print(f"[OK] Data saved to: {csv_path}")
                print(f"Total records: {len(result_df)}")
                
                return transacting_users
            else:
                print("[ERROR] Could not find Total transacting Users")
                print("\nDebugging - First 2000 chars of page text:")
                print(page_text[:2000])
                return None
                
        except Exception as e:
            print(f"[ERROR] Error occurred: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()
            print("\n[OK] Browser closed")

if __name__ == "__main__":
    asyncio.run(scrape_groww_data())
