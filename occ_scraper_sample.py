import pandas as pd
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load filtered file (start with a few rows for testing)
df = pd.read_csv("filtered_ticker_changes.csv").head(10)

# Selenium setup
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://infomemo.theocc.com/infomemo/search")

# Date range
start_date = "01/01/2015"
end_date = datetime.today().strftime("%m/%d/%Y")

# Helper to set posted date range
def set_date_range():
    try:
        start_input = driver.find_element(By.ID, "startpostdate")
        end_input = driver.find_element(By.ID, "endpostdate")
        driver.execute_script("arguments[0].value = arguments[1];", start_input, start_date)
        driver.execute_script("arguments[0].value = arguments[1];", end_input, end_date)
        end_input.send_keys(Keys.TAB)
        time.sleep(1)
    except Exception as e:
        print("Date input error:", e)

# Wait and set date range once
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "startpostdate")))
set_date_range()

# Wait for search bar
search_box = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Searches all the text']"))
)

results = []

# Classification helper
def classify_memo(title):
    title = title.lower()
    if "symbol change" in title or "name/symbol change" in title:
        if any(term in title for term in ["adjustment", "anticipated", "merger", "spin-off"]):
            return "Adjustment"
        else:
            return "Pure"
    elif "contract adjustment" in title:
        return "Adjustment"
    elif "error" in title:
        return "Error"
    elif "not found" in title:
        return "Not Found"
    return "Unknown"

for idx, row in df.iterrows():
    old_ticker = row['Old Ticker']
    new_ticker = row['New Ticker']
    search_term = f"{old_ticker} {new_ticker}"

    try:
        # Re-locate search box freshly each time
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Searches all the text']"))
        )
        # Clear search box, enter new term
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        # Wait for results to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "mainSearchResults"))
        )
        time.sleep(2)

        memo_divs = driver.find_elements(By.CSS_SELECTOR, "div.row.memoContent")
        found = False

        for memo in memo_divs:
            cols = memo.find_elements(By.CLASS_NAME, "informationMemo-Column")
            if len(cols) >= 4:
                post_date = cols[1].text.strip()
                effective_date = cols[2].text.strip()
                title = cols[3].text.strip()

                classification = classify_memo(title)

                results.append({
                    "Old Ticker": old_ticker,
                    "New Ticker": new_ticker,
                    "Search Term": search_term,
                    "Memo Title": title,
                    "Effective Date": effective_date,
                    "Post Date": post_date,
                    "Classification": classification
                })
                found = True

        if not found:
            results.append({
                "Old Ticker": old_ticker,
                "New Ticker": new_ticker,
                "Search Term": search_term,
                "Memo Title": "Not found",
                "Effective Date": "",
                "Post Date": "",
                "Classification": "Not Found"
            })

    except Exception as e:
        print(f"Error on {search_term}: {e}")
        results.append({
            "Old Ticker": old_ticker,
            "New Ticker": new_ticker,
            "Search Term": search_term,
            "Memo Title": "Error",
            "Effective Date": "",
            "Post Date": "",
            "Classification": "Error"
        })

    time.sleep(1)

driver.quit()

# Save to CSV
output_df = pd.DataFrame(results)
output_df.to_csv("occ_classified_results.csv", index=False)
print("✅ Done. Results saved to occ_classified_results.csv")
