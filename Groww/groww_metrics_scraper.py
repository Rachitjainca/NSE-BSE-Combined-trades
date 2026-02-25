#!/usr/bin/env python3
"""
Groww Investor Relations Comprehensive Data Scraper
Fetches multiple metrics from https://groww.in/investor-relations:
- Total Transacting Users
- Total Customer Assets
- Stocks Turnover
- Equity Derivatives Premium Turnover
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
from playwright.async_api import async_playwright, TimeoutError

class GrowwComprehensiveScraper:
    def __init__(self):
        self.url = "https://groww.in/investor-relations"
        self.csv_path = "groww_metrics_data.csv"
        
    async def run(self):
        """Main scraper execution"""
        print("[*] Groww Investor Relations Comprehensive Scraper")
        print(f"[*] URL: {self.url}")
        print("=" * 70)
        
        async with async_playwright() as playwright:
            browser = None
            try:
                # Launch browser
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
                print("[*] Waiting for content to render (8 seconds)...")
                await page.wait_for_timeout(8000)
                
                # Extract all metrics
                print("\n[*] Extracting metrics...")
                metrics = await self._extract_all_metrics(page)
                
                if metrics:
                    print("\n" + "=" * 70)
                    print("[SUCCESS] Extracted Metrics:")
                    print("=" * 70)
                    for key, value in metrics.items():
                        print(f"  {key}: {value}")
                    print("=" * 70)
                    
                    self._save_data(metrics)
                    return True
                else:
                    print("\n[!] Failed to extract metrics")
                    return False
                    
            except TimeoutError:
                print("[!] Page loading timed out")
                return False
            except Exception as e:
                print(f"[!] Error: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                return False
            finally:
                if browser:
                    await browser.close()
                    print("\n[+] Browser closed")
    
    async def _extract_all_metrics(self, page):
        """Extract all metrics from the page"""
        metrics = {}
        
        # Get page text
        page_text = await page.locator('body').text_content()
        lines = [l.strip() for l in page_text.split('\n') if l.strip()]
        
        # Define metrics to search for
        metric_patterns = {
            'Total Transacting Users': None,
            'Total Customer Assets': None,
            'Stocks Turnover': None,
            'Equity Derivatives Premium Turnover': None,
        }
        
        # Search for each metric
        for i, line in enumerate(lines):
            for metric_name in metric_patterns.keys():
                if metric_name in line and not metric_patterns[metric_name]:
                    # Look in nearby lines for the value
                    print(f"[*] Found '{metric_name}' at line {i}")
                    
                    # Check next few lines
                    for j in range(i + 1, min(i + 10, len(lines))):
                        next_line = lines[j]
                        
                        # Look for numbers with currency symbols or M/K suffixes
                        if any(c in next_line for c in ['₹', 'Million', ',', '0123456789']):
                            # Skip if it's a date or known false positive
                            if next_line not in ['24', '2026', '2025', '30', 'PM', 'AM']:
                                # Extract the potential value
                                if len(next_line) > 0:
                                    metric_patterns[metric_name] = next_line
                                    print(f"    -> Value: {next_line}")
                                    break
        
        # Try alternative extraction using divs
        if not all(metric_patterns.values()):
            print("\n[*] Trying alternative extraction method...")
            metrics_found = await self._extract_by_selectors(page)
            # Merge with existing results
            for key in metric_patterns:
                if key not in metrics or not metrics[key]:
                    if key in metrics_found:
                        metric_patterns[key] = metrics_found[key]
        
        return {k: v for k, v in metric_patterns.items() if v}
    
    async def _extract_by_selectors(self, page):
        """Try to extract by CSS selectors"""
        metrics = {}
        
        try:
            # Get all divs that might contain metrics
            divs = await page.locator('div').all()
            
            metric_keywords = {
                'Transacting Users': [],
                'Customer Assets': [],
                'Stocks Turnover': [],
                'Derivatives': []
            }
            
            for div in divs[:200]:
                try:
                    text = await div.text_content()
                    if text:
                        for keyword in metric_keywords:
                            if keyword.lower() in text.lower():
                                metric_keywords[keyword].append(text.strip())
                except:
                    pass
            
            # Process results
            if metric_keywords['Transacting Users']:
                metrics['Total Transacting Users'] = metric_keywords['Transacting Users'][0][:50]
            if metric_keywords['Customer Assets']:
                metrics['Total Customer Assets'] = metric_keywords['Customer Assets'][0][:50]
            if metric_keywords['Stocks Turnover']:
                metrics['Stocks Turnover'] = metric_keywords['Stocks Turnover'][0][:50]
            if metric_keywords['Derivatives']:
                metrics['Equity Derivatives Premium Turnover'] = metric_keywords['Derivatives'][0][:50]
                
        except Exception as e:
            print(f"[-] Selector extraction failed: {e}")
        
        return metrics
    
    def _save_data(self, metrics):
        """Save metrics to CSV"""
        timestamp = datetime.now()
        
        row = {
            'Timestamp': timestamp.isoformat(),
            'Date': timestamp.strftime('%Y-%m-%d'),
            'Time': timestamp.strftime('%H:%M:%S'),
        }
        
        # Add metrics to row
        row.update(metrics)
        
        # Load existing data or create new
        if Path(self.csv_path).exists():
            df = pd.read_csv(self.csv_path)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])
        
        df.to_csv(self.csv_path, index=False)
        print(f"\n[+] Data saved to: {self.csv_path}")
        print(f"[+] Total records: {len(df)}")
        print(f"\nDataframe columns: {list(df.columns)}")
        print(f"\nLatest entry:\n{df.iloc[-1]}")

async def main():
    scraper = GrowwComprehensiveScraper()
    success = await scraper.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
