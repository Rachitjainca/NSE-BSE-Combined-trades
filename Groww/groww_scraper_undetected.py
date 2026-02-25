import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
from datetime import datetime

def scrape_groww_data():
    """
    Scrape Total transacting Users from Groww Investor Relations page using undetected-chromedriver
    """
    url = "https://groww.in/investor-relations"
    xpath = '//*[@id="root"]/div[3]/div[1]/div/div[1]/div[1]/div[2]/span[1]'
    
    print(f"Starting web scraper for: {url}")
    print(f"Target XPath: {xpath}")
    print("=" * 50)
    
    driver = None
    try:
        # Use undetected-chromedriver which bypasses anti-bot protection
        print("Initializing undetected ChromeDriver...")
        driver = uc.Chrome(headless=False, use_subprocess=False)
        
        print(f"Loading page: {url}")
        driver.get(url)
        
        print(f"✓ Page loaded: {url}")
        
        # Wait for the element to be present (max 20 seconds)
        print("\nWaiting for element to load...")
        wait = WebDriverWait(driver, 20)
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        
        # Get the text
        data_value = element.text.strip()
        
        print(f"✓ Element found!")
        print(f"\n{'='*50}")
        print(f"✅ Total transacting Users: {data_value}")
        print(f"{'='*50}\n")
        
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
        print(f"✓ Data saved to: {csv_path}")
        print(f"Total records: {len(result_df)}")
        
        return data_value
        
    except TimeoutException:
        print("❌ Error: Element not found within timeout (20 seconds)")
        print("The page structure may have changed or the element is not visible")
        if driver:
            print("\nHTML of page:")
            print(driver.page_source[:1000])
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
