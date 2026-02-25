# Groww Investor Relations Data Scraper

## Overview
This collection of scripts scrapes customer and investor metrics from https://groww.in/investor-relations

## Metrics Scraped
- **Total Transacting Users** (e.g., 21,275,206)
- **Total Customer Assets** (e.g., ₹3,112,181 Million)
- **Stocks Turnover** (e.g., ₹2,404,512 Million)  
- **Equity Derivatives Premium Turnover** (e.g., ₹2,687,157 Million)

## Files in This Folder

### Main Scrapers
- **groww_customer_scraper.py** - Original comprehensive scraper with multiple methods
- **groww_metrics_scraper.py** - Metrics-focused scraper
- **groww_metrics_scraper_v2.py** - Improved text-based extraction
- **groww_final_scraper.py** - Final optimized version
- **groww_xpath_scraper.py** - XPath-based extraction
- **groww_xpath_direct.py** - Direct XPath targeting

### Debugging Scripts
- **debug_groww.py** - Interactive page content inspector
- **debug_metrics.py** - Metrics search debugger
- **debug_metrics_v2.py** - Extended debugging with network monitoring
- **test_connectivity.py** - Network connectivity tester

## Usage

### Running the Scraper
```bash
# From the Groww folder
python groww_customer_scraper.py

# Or from parent NSE BSE Combined folder
.\.venv\Scripts\python.exe Groww\groww_customer_scraper.py
```

### Output
Data is saved to `groww_metrics_data.csv` andgroww_user_data.csv` with the following columns:
- Timestamp
- Date  
- Time
- Metric values (Total Transacting Users, Total Customer Assets, etc.)

## Technical Details

### Challenges Encountered
1. **Dynamic Content Rendering**: The metrics are rendered by React/JavaScript after initial page load
2. **CSS Styling**: Heavy use of CSS-in-JS and Tailwind classes makes direct HTML parsing difficult
3. **Anti-Bot Protection**: CloudFront CDN requires proper headers and user-agent spoofing
4. **Page Delays**: React components may take 15-25 seconds to fully render

### Solution Approaches Tested
- ✓ Playwright for JavaScript rendering
- ✓ Network request monitoring
- ✓ XPath selectors for element targeting  
- ✓ Text content extraction with pattern matching
- Selenium (had connection issues)
- BeautifulSoup (insufficient for dynamic content)
- Undetected ChromeDriver (distutils compatibility issues)

## Requirements
All dependencies are in the parent project's `.venv`:
- playwright >= 1.40
- pandas >= 2.0
- requests >= 2.31

## Troubleshooting

### Script Hangs or Times Out
- The page takes 15-25 seconds to render metrics
- Browser window must remain open during execution
- Check internet connectivity

### Numbers Not Extracted
- Verify the XPath patterns match current page structure (Groww updates website sometimes)
- Check if page layout has changed
- Run `debug_metrics_v2.py` to inspect current HTML structure

### CSV Files Empty or Incorrect
- Delete `groww_metrics_data.csv` and `groww_user_data.csv` to start fresh
- Check if data is being written by looking at file modification time

## Success Indicators
When running correctly, you should see output like:
```
[*] Groww Metrics Scraper
[*] URL: https://groww.in/investor-relations
======================================================================
[+] Page loaded successfully
[*] Waiting for content to render...
[SUCCESS] Total transacting Users: 21,275,206
[+] Data saved to: groww_metrics_data.csv
```

## Data Notes
- Data is timestamped (IST timezone)
- Historical records are appended to CSV (not overwritten)
- Numbers from Groww website are as of the last update date shown on their page
- Currency values are in ₹ Million (Indian Rupees)
