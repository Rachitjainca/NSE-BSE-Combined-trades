#!/usr/bin/env python3
"""
Groww Metrics Scraper – Extended Wait and Network Inspection
Waits longer and inspects network requests to find data source
"""

import asyncio
from playwright.async_api import async_playwright
import json
import time

async def scrape_with_network():
    """Scrape with network monitoring"""
    url = "https://groww.in/investor-relations"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Monitor API requests
        responses = []
        async def handle_response(response):
            if 'api' in response.url or 'json' in response.url:
                try:
                    text = await response.text()
                    responses.append({'url': response.url, 'data': text[:500]})
                except:
                    pass
        
        page.on('response', handle_response)
        
        print("[*] Loading page with network monitoring...")
        start_time = time.time()
        await page.goto(url, wait_until='networkidle', timeout=60000)
        load_time = time.time() - start_time
        print(f"[+] Page loaded in {load_time:.2f} seconds")
        
        print("\n[*] Waiting longer for JavaScript rendering (15 seconds)...")
        await page.wait_for_timeout(15000)
        
        # Now search for the metrics
        print("\n[*] Searching for metrics in rendered page...")
        
        html = await page.content()
        
        # Look for larger context around metrics
        metrics_patterns = [
            'Total Transacting Users',
            'Total Customer Assets',
            'Stocks Turnover',
            '21,275,206',
            '3,112,181',
            '2,404,512',
            '2,687,157',
        ]
        
        for pattern in metrics_patterns:
            if pattern.lower() in html.lower():
                print(f"[+] Found: {pattern}")
                idx = html.lower().find(pattern.lower())
                context = html[max(0, idx-150):min(len(html), idx+150)]
                print(f"    Context: {context[:200]}")
        
        # Try to get all div content
        print("\n[*] Getting all rendered text content...")
        all_text = await page.locator('body').text_content()
        
        # Search in all text
        lines = all_text.split('\n')
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if line_clean and (
                'Transacting' in line_clean or 
                'Customer Assets' in line_clean or 
                'Turnover' in line_clean or
                any(c in line_clean for c in ['21', '3,1', '2,4', '2,6'])
            ):
                print(f"Line {i}: {line_clean[:100]}")
        
        # Try to wait for specific selectors
        print("\n[*] Waiting for main content div...")
        try:
            await page.wait_for_selector('[class*="customer"], [class*="metric"], [class*="stat"]', timeout=5000)
            print("[+] Found content divs")
        except:
            print("[-] Could not find content selectors")
        
        # Print network requests
        if responses:
            print(f"\n[*] Found {len(responses)} API requests:")
            for resp in responses[:5]:
                print(f"    {resp['url'][:80]}")
                if 'transact' in resp['data'].lower() or 'customer' in resp['data'].lower():
                    print(f"    DATA: {resp['data'][:200]}")
        
        await browser.close()

asyncio.run(scrape_with_network())
