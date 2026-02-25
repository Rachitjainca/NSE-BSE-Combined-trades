#!/usr/bin/env python3
"""
Groww Debug - Inspect actual page content
"""

import asyncio
from playwright.async_api import async_playwright

async def debug():
    url = "https://groww.in/investor-relations"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.set_viewport_size({"width": 1920, "height": 1080})
        print("[*] Loading...")
        await page.goto(url, wait_until='load')
        print("[+] Loaded")
        
        # Wait and extract
        print("[*] Waiting 5 seconds...")
        await page.wait_for_timeout(5000)
        
        text = await page.locator('body').text_content()
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        print(f"\n[*] Found {len(lines)} non-empty lines of text")
        print("[*] Lines containing numbers or key words:\n")
        
        for i, line in enumerate(lines):
            # Show lines with numbers or metrics keywords
            if any(word in line.lower() for word in ['total', 'transact', 'customer', 'asset', 'turnover', 'stock', 'deriv', 'equity']):
                print(f"{i:3d}: {line[:100]}")
            elif any(c in line for c in '0123456789₹'):
                print(f"{i:3d}: {line[:100]}")
        
        print("\n[*] First 100 lines:")
        for i, line in enumerate(lines[:100]):
            print(f"{i:3d}: {line[:100]}")
        
        await browser.close()

asyncio.run(debug())
