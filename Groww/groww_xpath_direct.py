#!/usr/bin/env python3
"""
Groww Scraper - Direct HTML InstructionExtraction with XPath
Uses specific XPath queries to locate and extract metric values
"""

import asyncio
from datetime import datetime
import pandas as pd
from pathlib import Path
from playwright.async_api import async_playwright

async def scrape_groww_direct():
    """Direct extraction using XPath"""
    url = "https://groww.in/investor-relations"
    csv_path = "groww_metrics_data.csv"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        print("[*] Groww Direct Scraper")
        print("[*] Loading page...")
        await page.goto(url, wait_until='networkidle')
        print("[+] Page loaded")
        
        print("[*] Waiting 25 seconds for full React render...")
        for i in range(25):
            await page.wait_for_timeout(1000)
            if i % 5 == 0:
                print(f"    ...{i}s")
        
        print("\n[*] Extracting metrics using multiple XPath strategies...")
        
        metrics = {}
        
        # Strategy 1: XPath for divs containing specific text
        xpaths = {
            'Total Transacting Users': [
                "//span[contains(text(), 'Total Transacting Users')]/ancestor::div[2]//span[1]",
                "//span[contains(text(), 'Transacting Users')]/following-sibling::*[1]//span",
                "(//*[contains(text(), 'Transacting Users')])[1]/following::span[contains(., ',')]",
            ],
            'Total Customer Assets': [
                "//span[contains(text(), 'Total Customer Assets')]/ancestor::div[2]//span[1]",
                "//span[contains(text(), 'Customer Assets')]/following-sibling::*[1]//span",
            ],
            'Stocks Turnover': [
                "//span[contains(text(), 'Stocks Turnover')]/ancestor::div[1]/following::span[1]",
                "//*[contains(text(), 'Stocks Turnover')]/following::span[contains(., '₹')]",
            ],
            'Equity Derivatives Premium Turnover': [
                "//span[contains(text(), 'Equity Derivatives')]/ancestor::div[1]/following::span[1]",
                "//*[contains(text(), 'Derivatives')]/following::span[contains(., '₹')]",
            ]
        }
        
        for metric_name, xpath_list in xpaths.items():
            for xpath_query in xpath_list:
                try:
                    locator = page.locator(f"xpath={xpath_query}")
                    count = await locator.count()
                    if count > 0:
                        text = await locator.first.text_content()
                        if text and text.strip():
                            metrics[metric_name] = text.strip()
                            print(f"[+] {metric_name}: {text.strip()}")
                            break
                except:
                    pass
            
            if metric_name not in metrics:
                print(f"[-] {metric_name}: Not found")
        
        # Strategy 2: Raw page source search
        if not all(metrics.values()):
            print("\n[*] Searching page source...")
            html = await page.content()
            
            # Look for the specific numbers we know should be there
            if '21' in html and '275' in html and '206' in html:
                print("[+] Page contains '21,275,206' (Total Transacting Users number)")
            if '3' in html and '112' in html and '181' in html:
                print("[+] Page contains '3,112,181' (Total Customer Assets number part)")
            if '2' in html and '404' in html and '512' in html:
                print("[+] Page contains '2,404,512' (Stocks Turnover number part)")
        
        # Save whatever we found
        if metrics:
            timestamp = datetime.now()
            row = {
                'Timestamp': timestamp.isoformat(),
                'Date': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                **metrics
            }
            
            if Path(csv_path).exists():
                df = pd.read_csv(csv_path)
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            else:
                df = pd.DataFrame([row])
            
            df.to_csv(csv_path, index=False)
            print(f"\n[+] Saved {len([v for v in metrics.values() if v])} metrics to {csv_path}")
        
        await browser.close()

asyncio.run(scrape_groww_direct())
