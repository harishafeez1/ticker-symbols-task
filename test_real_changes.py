import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Test with known real ticker changes (these should have OCC memos)
test_cases = [
    "META",  # Facebook name change
    "PYPL",  # PayPal
    "GOOGL", # Google/Alphabet
    "symbol change",  # Generic search
]

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage") 
options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://infomemo.theocc.com/infomemo/search")
    time.sleep(3)
    
    search_box = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Searches all the text']"))
    )
    
    for search_term in test_cases:
        print(f"\n🔍 Testing search: '{search_term}'")
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.submit()
        time.sleep(4)
        
        try:
            memo_divs = driver.find_elements(By.CSS_SELECTOR, "div.row.memoContent")
            print(f"📄 Found {len(memo_divs)} results")
            
            for i, memo in enumerate(memo_divs[:2]):
                try:
                    cols = memo.find_elements(By.CLASS_NAME, "informationMemo-Column")
                    if len(cols) >= 4:
                        title = cols[3].text.strip()
                        print(f"  • {title[:80]}...")
                except:
                    print(f"  • [Error reading result {i+1}]")
                    
        except Exception as e:
            print(f"❌ Search failed: {e}")
            
        # Navigate back to search
        driver.get("https://infomemo.theocc.com/infomemo/search")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Searches all the text']"))
        )
        
finally:
    driver.quit()