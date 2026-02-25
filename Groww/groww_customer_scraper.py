#!/usr/bin/env python3
"""
Groww Investor Relations Data Scraper
Fetches "Total Transacting Users" data from https://groww.in/investor-relations
"""

import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from playwright.async_api import async_playwright, TimeoutError

class GrowwScraper:
    def __init__(self):
        self.url = "https://groww.in/investor-relations"
        self.xpath = '//*[@id="root"]/div[3]/div[1]/div/div[1]/div[1]/div[2]/span[1]'
        self.csv_path = "groww_user_data.csv"
        
    async def run(self):
        """Main scraper execution  """
        print("[*] Groww Investor Relations Data Scraper")
        print(f"[*] URL: {self.url}")
        print(f"[*] XPath: {self.xpath}")
        print("=" * 70)
        
        async with async_playwright() as playwright:
            browser = None
            try:
                # Launch browser with optimized settings
                browser = await playwright.chromium.launch(
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = await browser.new_page()
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                # Navigate to page
                print("\n[*] Loading page...")
                await page.goto(self.url, wait_until='networkidle', timeout=60000)
                print("[+] Page loaded successfully")
                
                # Wait for dynamic content
                print("[*] Waiting for content to render (10 seconds)...")
                await page.wait_for_timeout(10000)
                
                # Extract data
                data_value = await self._extract_data(page)
                
                if data_value:
                    print("\n" + "=" * 70)
                    print(f"[SUCCESS] Total Transacting Users: {data_value}")
                    print("=" * 70)
                    self._save_data(data_value)
                    return True
                else:
                    print("\n[!] Failed to extract data")
                    return False
                    
            except TimeoutError:
                print("[!] Page loading timed out")
                return False
            except Exception as e:
                print(f"[!] Error: {type(e).__name__}: {e}")
                return False
            finally:
                if browser:
                    await browser.close()
                    print("\n[+] Browser closed")
    
    async def _extract_data(self, page):
        """Extract data using multiple methods"""
        methods = [
            ("XPath", self._extract_by_xpath),
            ("CSS Selector", self._extract_by_selector),
            ("Text Search", self._extract_by_text),
        ]
        
        for method_name, method_func in methods:
            print(f"\n[*] Trying {method_name} method...")
            try:
                result = await method_func(page)
                if result:
                    print(f"[+] {method_name} succeeded: {result}")
                    return result
            except Exception as e:
                print(f"[-] {method_name} failed: {e}")
        
        return None
    
    async def _extract_by_xpath(self, page):
        """Extract using XPath"""
        try:
            locator = page.locator(f'xpath={self.xpath}')
            await locator.wait_for(timeout=5000)
            text = await locator.text_content()
            return text.strip() if text else None
        except Exception as e:
            raise Exception(f"XPath extraction failed: {e}")
    
    async def _extract_by_selector(self, page):
        """Extract using CSS selectors related to the div structure"""
        try:
            # Try to find span elements in root div
            spans = await page.locator('#root div span').all()
            for span in spans[:20]:
                text = await span.text_content()
                if text and any(c in text for c in ['M', 'K', '0123456789']):
                    text_clean = text.strip()
                    if len(text_clean) > 0 and text_clean not in ['M', 'K']:
                        return text_clean
        except Exception as e:
            raise Exception(f"CSS selector extraction failed: {e}")
    
    async def _extract_by_text(self, page):
        """Extract by searching page text"""
        try:
            page_text = await page.locator('body').text_content()
            lines = page_text.split('\n')
            
            for i, line in enumerate(lines):
                if 'Total Transacting Users' in line or 'transacting' in line.lower():
                    # Check next lines for data
                    for j in range(i+1, min(i+6, len(lines))):
                        next_line = lines[j].strip()
                        # Look for numbers with M/K suffix
                        if next_line and any(c in next_line for c in ['M', 'K', '0123456789']):
                            # Filter out date-like numbers
                            if next_line not in ['30', '2025', '2026', '9']:
                                return next_line
        except Exception as e:
            raise Exception(f"Text search extraction failed: {e}")
    
    def _save_data(self, value):
        """Save data to CSV"""
        timestamp = datetime.now()
        new_row = {
            'Date': timestamp,
            'Total_Transacting_Users': value,
            'Timestamp': timestamp.isoformat()
        }
        
        # Load existing data if available
        if Path(self.csv_path).exists():
            df = pd.read_csv(self.csv_path)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])
        
        df.to_csv(self.csv_path, index=False)
        print(f"[+] Data saved to: {self.csv_path}")
        print(f"[+] Total records: {len(df)}")

async def main():
    scraper = GrowwScraper()
    success = await scraper.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
