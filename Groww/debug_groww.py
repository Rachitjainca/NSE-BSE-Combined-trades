import asyncio
from playwright.async_api import async_playwright

async def debug_page():
    """
    Debug script to see what Groww page actually contains
    """
    url = "https://groww.in/investor-relations"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto(url, wait_until='networkidle', timeout=60000)
        
        # Wait for JS to render
        await page.wait_for_timeout(5000)
        
        # Get text around "Total Transacting Users"
        page_text = await page.locator('body').text_content()
        lines = page_text.split('\n')
        
        print("=" * 80)
        print("Looking for 'Total Transacting Users' section...")
        print("=" * 80)
        
        for i, line in enumerate(lines):
            if 'transacting' in line.lower():
                # Print 10 lines around this
                start = max(0, i - 3)
                end = min(len(lines), i + 7)
                
                print(f"\n[Found at line {i}]")
                for j in range(start, end):
                    marker = " >>> " if j == i else "     "
                    print(f"{marker} {j}: {lines[j][:120]}")
        
        # Also try to evaluate JavaScript to get the actual value
        print("\n" + "=" * 80)
        print("Trying to extract via JavaScript locators...")
        print("=" * 80)
        
        try:
            # Get all span elements
            spans = await page.locator('span').all()
            print(f"Found {len(spans)} span elements")
            
            for i, span in enumerate(spans[:50]):  
                text = await span.text_content()
                if text and text.strip() and len(text.strip()) < 50:
                    # Check if this might be our number
                    if any(c in text for c in ['M', 'K', '0123456789']) and text.strip() != 'M':
                        print(f"Span {i}: '{text.strip()}'")
        except Exception as e:
            print(f"Error getting spans: {e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_page())
