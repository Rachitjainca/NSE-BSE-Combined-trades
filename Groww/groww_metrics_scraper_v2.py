#!/usr/bin/env python3
"""
Groww Investor Relations Data Scraper - Targeted Extraction
Scrapes: Total Transacting Users, Total Customer Assets, Stocks Turnover, Equity Derivatives Premium Turnover
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import re
from playwright.async_api import async_playwright

class GrowwTargetedScraper:
    def __init__(self):
        self.url = "https://groww.in/investor-relations"
        self.csv_path = "groww_metrics_data.csv"
        
    async def run(self):
        """Main scraper execution"""
        print("[*] Groww Metrics Scraper (Targeted)")
        print(f"[*] URL: {self.url}")
        print("=" * 70)
        
        async with async_playwright() as playwright:
            browser = None
            try:
                browser = await playwright.chromium.launch(headless=False)
                page = await browser.new_page()
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                print("\n[*] Loading page...")
                await page.goto(self.url, wait_until='networkidle', timeout=60000)
                print("[+] Page loaded successfully")
                
                print("[*] Waiting for content (10 seconds)...")
                await page.wait_for_timeout(10000)
                
                # Extract metrics
                print("\n[*] Extracting metrics...")
                metrics = await self._extract_metrics(page)
                
                if metrics and any(metrics.values()):
                    print("\n" + "=" * 70)
                    print("[SUCCESS] Metrics Extracted:")
                    print("=" * 70)
                    for key, value in metrics.items():
                        status = "[+]" if value else "[-]"
                        print(f"{status} {key}: {value}")
                    print("=" * 70)
                    
                    self._save_data(metrics)
                    return True
                else:
                    print("\n[!] No metrics extracted")
                    return False
                    
            except Exception as e:
                print(f"[!] Error: {type(e).__name__}: {e}")
                return False
            finally:
                if browser:
                    await browser.close()
                    print("\n[+] Browser closed")
    
    async def _extract_metrics(self, page):
        """Extract metrics using multiple strategies"""
        metrics = {
            'Total Transacting Users': None,
            'Total Customer Assets': None,
            'Stocks Turnover': None,
            'Equity Derivatives Premium Turnover': None,
        }
        
        # Strategy 1: Look for specific data in spans with numbers
        print("\n[*] Strategy 1: Looking for numbers in spans...")
        spans = await page.locator('span').all()
        
        number_pattern = re.compile(r'^\d{1,3}(?:[,\d]*)?$|^₹[\d,]+(?:\sMillion)?$')
        found_numbers = []
        
        for span in spans:
            try:
                text = await span.text_content()
                if text:
                    text = text.strip()
                    # Look for numbers or currency values
                    if re.search(r'^\d+(?:[,\d]+)?$', text) or '₹' in text or 'Million' in text:
                        found_numbers.append(text)
                        if len(found_numbers) <= 10:
                            print(f"    Found: {text}")
            except:
                pass
        
        # Strategy 2: Extract full page text and search for context
        print("\n[*] Strategy 2: Searching page text for metrics...")
        page_text = await page.locator('body').text_content()
        full_text = page_text
        
        # Extract numbers followed by their labels
        metric_searches = [
            (r'(\d{1,3}(?:[,\d]+)*)\s*Total Transacting Users', 'Total Transacting Users'),
            (r'(₹[\d,]+\sMillion)\s*Total Customer Assets', 'Total Customer Assets'),
            (r'(₹[\d,]+\sMillion)\s*Stocks Turnover', 'Stocks Turnover'),
            (r'(₹[\d,]+\sMillion)\s*Equity Derivatives', 'Equity Derivatives Premium Turnover'),
        ]
        
        for pattern, metric_name in metric_searches:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                metrics[metric_name] = value
                print(f"    Found {metric_name}: {value}")
        
        # Strategy 3: Look for divs with metric labels
        print("\n[*] Strategy 3: Searching divs for metric labels...")
        divs = await page.locator('div').all()
        
        for i, div in enumerate(divs[:300]):
            try:
                text = await div.text_content()
                if text:
                    for metric_name in metrics.keys():
                        if metric_name.lower() in text.lower() and not metrics[metric_name]:
                            # Get text from nearby siblings
                            try:
                                # Try to get preceding text
                                preceding = await div.evaluate('el => el.textContent.split("\\n").filter(l => l.trim())[0]')
                                if preceding and re.search(r'[\d,₹]', preceding):
                                    metrics[metric_name] = preceding.strip()
                                    print(f"    Found {metric_name}: {preceding.strip()}")
                            except:
                                pass
            except:
                pass
        
        return metrics
    
    def _save_data(self, metrics):
        """Save metrics to CSV"""
        timestamp = datetime.now()
        
        row = {
            'Timestamp': timestamp.isoformat(),
            'Date': timestamp.strftime('%Y-%m-%d'),
            'Time': timestamp.strftime('%H:%M:%S'),
            **metrics
        }
        
        # Load existing or create new
        if Path(self.csv_path).exists():
            df = pd.read_csv(self.csv_path)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])
        
        df.to_csv(self.csv_path, index=False)
        print(f"\n[+] Data saved to: {self.csv_path}")
        print(f"[+] Total records: {len(df)}")

async def main():
    scraper = GrowwTargetedScraper()
    success = await scraper.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
