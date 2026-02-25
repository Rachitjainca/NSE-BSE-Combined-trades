#!/usr/bin/env python3
"""
Groww Metrics Debugger - Inspect HTML structure to find the data
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def debug_groww():
    """Debug the page structure"""
    url = "https://groww.in/investor-relations"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("[*] Loading page...")
        await page.goto(url, wait_until='networkidle', timeout=60000)
        print("[+] Page loaded")
        
        print("[*] Waiting for content...")
        await page.wait_for_timeout(10000)
        
        # Get HTML and look for specific patterns
        html = await page.content()
        
        # Print sections with metrics
        print("\n[*] Searching for metric values in HTML...")
        
        # Look for the specific numbers we know should be there
        import re
        
        numbers = [
            ('21,275,206', 'Total Transacting Users'),
            ('3,112,181', 'Total Customer Assets'),
            ('2,404,512', 'Stocks Turnover'),
            ('2,687,157', 'Equity Derivatives'),
        ]
        
        for number, metric in numbers:
            if number in html:
                print(f"[+] Found {metric}: {number}")
                # Get context around it
                idx = html.find(number)
                context = html[max(0, idx-200):min(len(html), idx+200)]
                print(f"    Context: {context}")
            else:
                print(f"[-] Not found: {metric} ({number})")
        
        # Try to extract all text content with better methods
        print("\n[*] Extracting page content...")
        
        # Get all spans with their IDs or classes
        spans = await page.query_selector_all('span')
        print(f"\n[*] Found {len(spans)} spans, checking first 100...")
        
        for i, span in enumerate(spans[:100]):
            text = await page.evaluate('el => el.textContent', span)
            if text and len(text.strip()) > 0 and len(text.strip()) < 100:
                # Check if it contains numbers
                if any(c in text for c in '0123456789,₹'):
                    print(f"    Span {i}: {text.strip()[:80]}")
        
        # Try to extract using JavaScript - evaluate specific HTML paths
        print("\n[*] Trying JavaScript extraction...")
        try:
            # Look for all divs with text content
            result = await page.evaluate('''() => {
                const metrics = {};
                const allText = document.body.innerText;
                
                // Create an array of all text nodes
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                let node;
                let count = 0;
                const texts = [];
                while(node = walker.nextNode()) {
                    const text = node.textContent.trim();
                    if (text.length > 0 && text.length < 100) {
                        texts.push(text);
                        if (texts.length < 50) {
                            count++;
                        }
                    }
                }
                
                return texts.slice(0, 50);
            }''')
            
            print("Text elements on page:")
            for i, text in enumerate(result):
                if any(c in text for c in '0123456789,₹'):
                    print(f"    {i}: {text[:100]}")
        except Exception as e:
            print(f"[-] JS extraction failed: {e}")
        
        await browser.close()

asyncio.run(debug_groww())
