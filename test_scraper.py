import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Test with just one ticker
test_data = [{"Old Ticker": "FBMS", "New Ticker": "RNST"}]

# Browser setup with more options
options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage") 
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

print("🚀 Starting browser...")
driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    print("📝 Loading OCC search page...")
    driver.get("https://infomemo.theocc.com/infomemo/search")
    time.sleep(3)
    
    print("📅 Setting date range...")
    try:
        start_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "startpostdate")))
        end_input = driver.find_element(By.ID, "endpostdate")
        driver.execute_script("arguments[0].value = arguments[1];", start_input, "01/01/2015")
        driver.execute_script("arguments[0].value = arguments[1];", end_input, "12/31/2025")
        end_input.send_keys(Keys.TAB)
        print("✅ Date range set!")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Failed to set date range: {e}")
    
    print("🔍 Looking for search box...")
    search_box = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Searches all the text']"))
    )
    print("✅ Found search box!")
    
    # Test search
    search_term = "FBMS RNST"
    print(f"🔍 Searching for: {search_term}")
    search_box.clear()
    search_box.send_keys(search_term)
    search_box.submit()
    
    time.sleep(3)
    print("📊 Looking for results...")
    
    # Try to find results
    results_found = False
    try:
        results_div = driver.find_element(By.CLASS_NAME, "mainSearchResults")
        print("✅ Found results container")
        results_found = True
    except:
        print("❌ No results container found")
    
    if results_found:
        memo_divs = driver.find_elements(By.CSS_SELECTOR, "div.row.memoContent")
        print(f"📄 Found {len(memo_divs)} memo divs")
        
        for i, memo in enumerate(memo_divs[:3]):  # Just check first 3
            try:
                cols = memo.find_elements(By.CLASS_NAME, "informationMemo-Column")
                if len(cols) >= 4:
                    title = cols[3].text.strip()
                    print(f"  {i+1}. {title}")
            except Exception as e:
                print(f"  {i+1}. Error reading memo: {e}")
    
    print("🎯 Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
finally:
    print("🔚 Closing browser...")
    driver.quit()