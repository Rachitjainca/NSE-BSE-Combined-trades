import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

async def scrape_groww_data():
    """
    Scrape Total transacting Users from Groww Investor Relations page using Playwright
    """
    url = "https://groww.in/investor-relations"
    xpath = '//*[@id="root"]/div[3]/div[1]/div/div[1]/div[1]/div[2]/span[1]'
    
    print(f"Starting web scraper for: {url}")
    print(f"Target XPath: {xpath}")
    print("=" * 50)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Set user agent to mimic real browser
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        try:
            print(f"Loading page: {url}")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            print(f"✓ Page loaded: {url}")
            
            # Wait for element and get the value
            print("\nWaiting for element to load...")
            try:
                element = page.locator(f'xpath={xpath}')
                data_value = await element.text_content(timeout=20000)
                
                if data_value:
                    data_value = data_value.strip()
                    print(f"✓ Element found!")
                    print(f"\n{'='*50}")
                    print(f"✅ Total transacting Users: {data_value}")
                    print(f"{'='*50}\n")
                    
                    # Save to CSV
                    timestamp = datetime.now()
                    result_df = pd.DataFrame({
                        'Date': [timestamp],
                        'Total_Transacting_Users': [data_value],
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
                    
                    return data_value
                else:
                    print("❌ Error: Element text is empty")
                    return None
                    
            except Exception as e:
                print(f"❌ Error finding/reading element: {type(e).__name__}: {e}")
                # Print page content for debugging
                content = await page.content()
                print(f"\nFirst 2000 characters of page content:")
                print(content[:2000])
                return None
        finally:
            await browser.close()
            print("\n✓ Browser closed")

if __name__ == "__main__":
    asyncio.run(scrape_groww_data())
