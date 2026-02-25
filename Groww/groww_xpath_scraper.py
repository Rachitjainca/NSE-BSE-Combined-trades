import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from datetime import datetime

async def scrape_groww_with_xpath():
    """
    Scrape Groww using the exact XPath provided
    """
    url = "https://groww.in/investor-relations"
    # The XPath provided by user
    xpath = '//*[@id="root"]/div[3]/div[1]/div/div[1]/div[1]/div[2]/span[1]'
    
    print(f"Starting web scraper for: {url}")
    print(f"Target XPath: {xpath}")
    print("=" * 60)
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
            page = await browser.new_page()
            
            # Set viewport size
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            print("Loading page (this may take 15-30 seconds)...")
            await page.goto(url, wait_until='networkidle', timeout=60000)
            
            print("[OK] Page loaded successfully")
            print("\nWaiting for dynamic content to render (5 seconds)...")
            await page.wait_for_timeout(5000)
            
            # Try the exact XPath
            print("\nAttempting to extract data using XPath...")
            try:
                locator = page.locator(f'xpath={xpath}')
                await locator.wait_for(timeout=10000)
                text = await locator.text_content()
                
                if text:
                    text = text.strip()
                    print(f"[OK] Successfully extracted: {text}")
                    
                    # Save to CSV
                    timestamp = datetime.now()
                    result_df = pd.DataFrame({
                        'Date': [timestamp],
                        'Total_Transacting_Users': [text],
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
                    print(f"\n{'='*60}")
                    print(f"[SUCCESS] Total transacting Users: {text}")
                    print(f"{'='*60}")
                    print(f"[OK] Data saved to groww_user_data.csv")
                    print(f"Total records: {len(result_df)}")
                    return text
                else:
                    print("[ERROR] XPath found element but text is empty")
                    
            except Exception as e:
                print(f"[ERROR] Failed to extract via XPath: {e}")
                
                # Try alternative approaches
                print("\n[INFO] Trying alternative extraction methods...")
                
                # Get all divs and print their content
                page_text = await page.locator('body').text_content()
                lines = [l.strip() for l in page_text.split('\n') if l.strip()]
                
                # Look specifically for "Total Transacting Users"  pattern
                for i, line in enumerate(lines):
                    if 'Total Transacting Users' in line or 'transacting' in line.lower() and 'users' in line.lower():
                        print(f"\nFound relevant section at line {i}:")
                        for j in range(max(0, i-2), min(len(lines), i+8)):
                            print(f"  {lines[j][:100]}")
                        break
                        
            # Print page screenshot for manual inspection
            screenshot_path = "groww_page_screenshot.png"
            await page.screenshot(path=screenshot_path)
            print(f"[INFO] Page screenshot saved to: {screenshot_path}")
                        
        except asyncio.TimeoutError:
            print("[ERROR] Page loading timed out")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                await browser.close()
                print("\n[OK] Browser closed")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(scrape_groww_with_xpath())
