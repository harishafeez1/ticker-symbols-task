import os
import sys
import time
import pandas as pd
from datetime import datetime
from csv import DictWriter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException

# ========== CONFIG ==========
CHUNK_FILE = sys.argv[1] if len(sys.argv) > 1 else None
OUTPUT_DIR = "output"
MAX_RETRIES = 2
HEADLESS = True
START_DATE = "01/01/2015"
END_DATE = datetime.today().strftime("%m/%d/%Y")
# ============================

# Validate input
if not CHUNK_FILE or not os.path.exists(CHUNK_FILE):
    print("❌ Please provide a valid chunk CSV file path.")
    sys.exit(1)

# Prepare output
os.makedirs(OUTPUT_DIR, exist_ok=True)
chunk_id = os.path.splitext(os.path.basename(CHUNK_FILE))[0].split("_")[-1]
output_file = os.path.join(OUTPUT_DIR, f"output_{chunk_id}.csv")

# Skip if already complete
if os.path.exists(output_file):
    print(f"✅ Chunk {chunk_id} already processed. Skipping.")
    sys.exit(0)

df = pd.read_csv(CHUNK_FILE)

# ========== Classification Logic ==========
def classify_memo(title):
    title = title.lower()
    disqualifiers = [
        "adjustment", "anticipated", "merger", "spin-off", "split", "cusip",
        "reverse", "consolidation", "dividend"
    ]
    if "symbol change" in title or "name/symbol change" in title:
        if any(term in title for term in disqualifiers):
            return "Adjustment"
        import re
        match = re.search(r'new symbol:\s*([A-Z]+[0-9]+)', title.upper())
        if match:
            return "Adjustment"
        return "Pure"
    elif "contract adjustment" in title:
        return "Adjustment"
    return "Unknown"

# ========== Browser Setup ==========
options = Options()
if HEADLESS:
    options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1280x800")
driver = webdriver.Chrome(options=options)
driver.get("https://infomemo.theocc.com/infomemo/search")

# Set date filters
def set_date_range():
    try:
        start_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "startpostdate")))
        end_input = driver.find_element(By.ID, "endpostdate")
        driver.execute_script("arguments[0].value = arguments[1];", start_input, START_DATE)
        driver.execute_script("arguments[0].value = arguments[1];", end_input, END_DATE)
        end_input.send_keys(Keys.TAB)
        time.sleep(1)
    except Exception as e:
        print("❌ Failed to set date range:", e)

set_date_range()

# Prepare CSV writer
headers = ["Old Ticker", "New Ticker", "Search Term", "Memo Title", "Effective Date", "Post Date", "Classification"]
if not os.path.exists(output_file):
    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        DictWriter(f, fieldnames=headers).writeheader()

# ========== Main Loop ==========
for idx, row in df.iterrows():
    old_ticker = str(row['Old Ticker']).strip()
    new_ticker = str(row['New Ticker']).strip()
    search_term = f"{old_ticker} {new_ticker}"

    attempt = 0
    success = False

    while attempt <= MAX_RETRIES and not success:
        try:
            print(f"🔍 Searching: {search_term} (try {attempt + 1})")
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Searches all the text']"))
            )
            search_box.clear()
            search_box.send_keys(search_term)
            search_box.send_keys(Keys.RETURN)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "mainSearchResults"))
            )
            time.sleep(2)

            memo_divs = driver.find_elements(By.CSS_SELECTOR, "div.row.memoContent")
            print(f"🔎 Found {len(memo_divs)} result(s) for {search_term}")
            found = False

            for memo in memo_divs:
                try:
                    cols = memo.find_elements(By.CLASS_NAME, "informationMemo-Column")
                    if len(cols) >= 4:
                        post_date = cols[1].text.strip()
                        effective_date = cols[2].text.strip()
                        title = cols[3].text.strip()
                        classification = classify_memo(title)

                        row_data = {
                            "Old Ticker": old_ticker,
                            "New Ticker": new_ticker,
                            "Search Term": search_term,
                            "Memo Title": title,
                            "Effective Date": effective_date,
                            "Post Date": post_date,
                            "Classification": classification
                        }

                        with open(output_file, mode="a", newline="", encoding="utf-8") as f:
                            DictWriter(f, fieldnames=headers).writerow(row_data)
                        print(f"✅ Added memo: {title[:80]}... → {classification}")
                        found = True
                except StaleElementReferenceException:
                    print("⚠️ Stale element — skipping this memo")

            if not found:
                print(f"⚠️ No valid memos found for {search_term}")
                row_data = {
                    "Old Ticker": old_ticker,
                    "New Ticker": new_ticker,
                    "Search Term": search_term,
                    "Memo Title": "Not found",
                    "Effective Date": "",
                    "Post Date": "",
                    "Classification": "Not Found"
                }
                with open(output_file, mode="a", newline="", encoding="utf-8") as f:
                    DictWriter(f, fieldnames=headers).writerow(row_data)

            success = True

        except WebDriverException as e:
            print(f"❌ WebDriver error on {search_term}: {e}")
            attempt += 1
            time.sleep(2)
        except Exception as e:
            print(f"❌ Error on {search_term}: {e}")
            attempt += 1
            time.sleep(2)

    if not success:
        print(f"❌ Failed after retries: {search_term}")
        row_data = {
            "Old Ticker": old_ticker,
            "New Ticker": new_ticker,
            "Search Term": search_term,
            "Memo Title": "Error",
            "Effective Date": "",
            "Post Date": "",
            "Classification": "Error"
        }
        with open(output_file, mode="a", newline="", encoding="utf-8") as f:
            DictWriter(f, fieldnames=headers).writerow(row_data)

# ========== Done ==========
driver.quit()
print(f"✅ Done: All results written incrementally to {output_file}")
