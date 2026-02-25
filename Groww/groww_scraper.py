import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from datetime import datetime

def scrape_groww_data():
    """
    Scrape Total transacting Users from Groww Investor Relations page
    """
    url = "https://groww.in/investor-relations"
    xpath = '//*[@id="root"]/div[3]/div[1]/div/div[1]/div[1]/div[2]/span[1]'
    
    print(f"Starting web scraper for: {url}")
    print(f"Target XPath: {xpath}")
    print("=" * 50)
    
    # Initialize Chrome driver with options
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    try:
        # Use webdriver-manager to automatically download ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        
        print(f"\n✓ Page loaded: {url}")
        
        # Wait for the element to be present (max 15 seconds)
        print("\nWaiting for element to load...")
        wait = WebDriverWait(driver, 15)
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        
        # Get the text
        data_value = element.text.strip()
        
        print(f"✓ Element found!")
        print(f"\nTotal transacting Users: {data_value}")
        
        # Save to CSV
        timestamp = datetime.now()
        result_df = pd.DataFrame({
            'Date': [timestamp],
            'Total_Transacting_Users': [data_value],
            'Timestamp': [timestamp.isoformat()]
        })
        
        csv_path = "groww_user_data.csv"
        
        # Append to existing or create new
        try:
            existing_df = pd.read_csv(csv_path)
            result_df = pd.concat([existing_df, result_df], ignore_index=True)
        except FileNotFoundError:
            pass
        
        result_df.to_csv(csv_path, index=False)
        print(f"\n✓ Data saved to: {csv_path}")
        print(f"Total records: {len(result_df)}")
        
        return data_value
        
    except TimeoutException:
        print("❌ Error: Element not found within timeout (10 seconds)")
        print("The page structure may have changed or the element is not visible")
        return None
    except NoSuchElementException:
        print("❌ Error: XPath does not match any element")
        return None
    except Exception as e:
        print(f"❌ Error occurred: {type(e).__name__}: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("\n✓ Browser closed")

if __name__ == "__main__":
    scrape_groww_data()
