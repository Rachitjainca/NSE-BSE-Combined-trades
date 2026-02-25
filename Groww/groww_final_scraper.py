#!/usr/bin/env python3
"""
Groww Metrics Scraper - Final Optimized Version
Uses proper selectors to extract rendered metrics
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import re
from playwright.async_api import async_playwright

class GrowwMetricsScraper:
    def __init__(self):
        self.url = "https://groww.in/investor-relations"
        self.csv_path = "groww_metrics_data.csv"
        
    async def run(self):
        """Main execution"""
        print("[*] Groww Metrics Scraper (Final)")
        print(f"[*] URL: {self.url}")
        print("=" * 70)
        
        async with async_playwright() as playwright:
            browser = None
            try:
                browser = await playwright.chromium.launch(headless=False)
                page = await browser.new_page()
                await page.set_viewport_size({"width": 1920, "height": 1080})
                
                print("\n[*] Loading page...")
                await page.goto(self.url, wait_until='load', timeout=60000)
                print("[+] Page loaded")
                
                # Wait for JS rendering
                print("[*] Waiting for React components to render (20 seconds)...")
                await page.wait_for_timeout(20000)
                
                # Extract metrics
                metrics = await self._extract_metrics_optimized(page)
                
                if metrics and any(metrics.values()):
                    print("\n" + "=" * 70)
                    print("[SUCCESS] Metrics Extracted:")
                    print("=" * 70)
                    for key, value in metrics.items():
                        if value:
                            print(f"  [+] {key}: {value}")
                    print("=" * 70)
                    
                    self._save_data(metrics)
                    return True
                else:
                    print("\n[!] Failed to extract metrics")
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
    
    async def _extract_metrics_optimized(self, page):
        """Extract metrics with optimized method"""
        metrics = {
            'Total Transacting Users': None,
            'Total Customer Assets': None,
            'Stocks Turnover': None,
            'Equity Derivatives Premium Turnover': None,
        }
        
        # Get full page text
        full_text = await page.locator('body').text_content()
        
        # Split into lines and process
        lines = full_text.split('\n')
        clean_lines = [l.strip() for l in lines if l.strip()]
        
        print(f"\n[*] Analyzing {len(clean_lines)} text lines...")
        
        # Search strategy: Look for metric name, then find the number nearby
        for i, line in enumerate(clean_lines):
            # Check for metric indicators
            if 'Total Transacting Users' in line or ('Transacting' in line and 'Users' in line):
                # Look for numbers in next few lines
                for j in range(i, min(i + 5, len(clean_lines))):
                    next_line = clean_lines[j]
                    num_match = re.search(r'(\d{1,3}(?:[,\d]+)*)', next_line)
                    if num_match and len(next_line) < 50:  # Probably just the number
                        metrics['Total Transacting Users'] = next_line
                        print(f"    Found Total Transacting Users: {next_line}")
                        break
            
            # Total Customer Assets
            elif 'Total Customer Assets' in line or ('Customer' in line and 'Assets' in line):
                for j in range(i, min(i + 5, len(clean_lines))):
                    next_line = clean_lines[j]
                    if '₹' in next_line or 'Million' in next_line:
                        metrics['Total Customer Assets'] = next_line
                        print(f"    Found Total Customer Assets: {next_line}")
                        break
            
            # Stocks Turnover
            elif 'Stocks Turnover' in line or ('Stocks' in line and 'Turnover' in line):
                for j in range(i, min(i + 5, len(clean_lines))):
                    next_line = clean_lines[j]
                    if '₹' in next_line or 'Million' in next_line:
                        metrics['Stocks Turnover'] = next_line
                        print(f"    Found Stocks Turnover: {next_line}")
                        break
            
            # Equity Derivatives
            elif 'Equity Derivatives' in line or ('Derivatives' in line and 'Premium' in line):
                for j in range(i, min(i + 6, len(clean_lines))):
                    next_line = clean_lines[j]
                    if '₹' in next_line or 'Million' in next_line:
                        metrics['Equity Derivatives Premium Turnover'] = next_line
                        print(f"    Found Equity Derivatives Premium Turnover: {next_line}")
                        break
        
        # If we didn't find all metrics, try a different approach
        if not all(metrics.values()):
            print("\n[*] Using alternative extraction method...")
            # Look for pattern: word followed by number/amount
            for i in range(len(clean_lines) - 1):
                line = clean_lines[i]
                next_line = clean_lines[i + 1] if i + 1 < len(clean_lines) else ''
                
                # Check if current line is a metric name and next is likely the value
                if len(line) < 50 and len(next_line) < 50:
                    if 'Transacting' in line and not metrics['Total Transacting Users']:
                        if any(c in next_line for c in '0123456789'):
                            metrics['Total Transacting Users'] = next_line
                    elif 'assets' in line.lower() and not metrics['Total Customer Assets']:
                        if '₹' in next_line:
                            metrics['Total Customer Assets'] = next_line
                    elif 'turnover' in line.lower():
                        if '₹' in next_line:
                            if 'Stocks' in line:
                                metrics['Stocks Turnover'] = next_line
                            elif 'Derivatives' in line:
                                metrics['Equity Derivatives Premium Turnover'] = next_line
        
        return metrics
    
    def _save_data(self, metrics):
        """Save to CSV"""
        timestamp = datetime.now()
        
        row = {
            'Timestamp': timestamp.isoformat(),
            'Date': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            **{k: v for k, v in metrics.items() if v}
        }
        
        # Load or create
        if Path(self.csv_path).exists():
            df = pd.read_csv(self.csv_path)
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        else:
            df = pd.DataFrame([row])
        
        df.to_csv(self.csv_path, index=False)
        print(f"\n[+] Saved to: {self.csv_path}")
        print(f"[+] Total records: {len(df)}")

async def main():
    scraper = GrowwMetricsScraper()
    success = await scraper.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
