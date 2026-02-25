#!/usr/bin/env python3
"""
Groww Investor Relations Metrics Scraper - Production Version
Reliably extracts: Total Transacting Users, Customer Assets, Stocks Turnover, Equity Derivatives Premium Turnover
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
from playwright.async_api import async_playwright

async def scrape_groww_metrics():
    """Main scraper function"""
    url = "https://groww.in/investor-relations"
    csv_path = "groww_full_metrics.csv"
    
    print("[*] Groww Metrics Scraper - Production Version")
    print(f"[*] Target: {url}")
    print("=" * 70)
    
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Set viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Load page
            print("\n[*] Loading page... (this may take 30-40 seconds)")
            await page.goto(url, wait_until='load', timeout=90000)
            print("[+] Page loaded")
            
            # Wait for React to fully render metrics
            print("[*] Waiting for React to render metrics...")
            await page.wait_for_timeout(3000)
            
            # Get page source
            print("[*] Extracting data...")
            page_text = await page.locator('body').text_content()
            
            # Extract metrics from text
            metrics = extract_metrics_from_text(page_text)
            
            if metrics:
                print("\n" + "=" * 70)
                print("[SUCCESS] Metrics Extracted:")
                print("=" * 70)
                
                timestamp = datetime.now()
                
                for key, value in metrics.items():
                    if value:
                        print(f"  [+] {key}: {value}")
                
                # Save to CSV
                row = {
                    'Timestamp': timestamp.isoformat(),
                    'DateTime': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    **metrics
                }
                
                if Path(csv_path).exists():
                    df = pd.read_csv(csv_path)
                    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                else:
                    df = pd.DataFrame([row])
                
                df = df.drop_duplicates(subset=['DateTime'], keep='last')
                df.to_csv(csv_path, index=False)
                
                print(f"\n[+] Saved to: {csv_path}")
                print(f"[+] Total records: {len(df)}")
                print("=" * 70)
                
                return True
            else:
                print("\n[!] No metrics extracted - page structure may have changed")
                return False
                
        except Exception as e:
            print(f"\n[!] Error: {type(e).__name__}: {e}")
            return False
        finally:
            await browser.close()
            print("\n[+] Browser closed\n")

def extract_metrics_from_text(page_text):
    """Extract metrics from page text"""
    metrics = {
        'Total Transacting Users': None,
        'Total Customer Assets': None,
        'Stocks Turnover': None,
        'Equity Derivatives Premium Turnover': None,
    }
    
    lines = [l.strip() for l in page_text.split('\n') if l.strip()]
    
    # Search strategy: find metric names, then extract following numbers
    for i,  line in enumerate(lines):
        # Total Transacting Users
        if 'Total Transacting Users' in line:
            for j in range(i+1, min(i+6, len(lines))):
                if any(c in lines[j] for c in '0123456789') and len(lines[j]) < 30:
                    metrics['Total Transacting Users'] = lines[j]
                    break
        
        # Total Customer Assets
        elif 'Total Customer Assets' in line:
            for j in range(i+1, min(i+6, len(lines))):
                if ('₹' in lines[j] or 'Million' in lines[j]) and len(lines[j]) < 50:
                    metrics['Total Customer Assets'] = lines[j]
                    break
        
        # Stocks Turnover
        elif 'Stocks Turnover' in line and 'Premium' not in line:
            for j in range(i+1, min(i+6, len(lines))):
                if ('₹' in lines[j] or 'Million' in lines[j]) and len(lines[j]) < 50:
                    metrics['Stocks Turnover'] = lines[j]
                    break
        
        # Equity Derivatives Premium Turnover
        elif 'Equity Derivatives Premium Turnover' in line or ('Equity Derivatives' in line and 'Premium' in line):
            for j in range(i+1, min(i+6, len(lines))):
                if ('₹' in lines[j] or 'Million' in lines[j]) and len(lines[j]) < 50:
                    metrics['Equity Derivatives Premium Turnover'] = lines[j]
                    break
    
    return {k: v for k, v in metrics.items() if v is not None}

async def main():
    success = await scrape_groww_metrics()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[!] Fatal error: {e}")
        sys.exit(1)
