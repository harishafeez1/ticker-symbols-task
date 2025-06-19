import os
import pandas as pd
import re

# --- CONFIG ---
OUTPUT_DIR = "output"
OUTPUT_FILE = "final_classified_results.csv"

# --- Helper: Classification Logic ---
def classify_memo(title):
    if pd.isna(title):
        return "Unknown"

    title_lower = title.lower()
    title_upper = title.upper()

    # Comprehensive disqualifiers for non-pure changes
    disqualifiers = [
        "contract adjustment", "adjustment", "anticipated", "merger", "spin-off",
        "split", "cusip", "reverse", "consolidation", "dividend", "reorg",
        "fund", "etf"
    ]

    # If any disqualifier is in title, it's an Adjustment
    if any(term in title_lower for term in disqualifiers):
        return "Adjustment"

    # Check if new symbol ends with number (e.g., "XYZ1")
    if re.search(r'new symbol:\s*([A-Z]+[0-9]+)', title_upper):
        return "Adjustment"

    # Classify as Pure only if symbol change is explicitly mentioned
    if "symbol change" in title_lower or "name/symbol change" in title_lower:
        return "Pure"

    return "Unknown"

# --- Step 1: Load and Merge ---
all_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("output_") and f.endswith(".csv")]
print(f"📦 Found {len(all_files)} chunk files.")

dfs = []
for file in all_files:
    df = pd.read_csv(os.path.join(OUTPUT_DIR, file))
    dfs.append(df)

full_df = pd.concat(dfs, ignore_index=True)
print(f"🔍 Merged total rows: {len(full_df)}")

# --- Step 2: Re-classify ---
full_df["Classification"] = full_df["Memo Title"].apply(classify_memo)

# --- Step 3: Save Output ---
full_df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Done. Saved reclassified results to: {OUTPUT_FILE}")


# --- Step 4: Save Only "Pure" Records ---
pure_df = full_df[full_df["Classification"] == "Pure"]
pure_output = "final_pure_ticker_changes.csv"
pure_df.to_csv(pure_output, index=False)
print(f"✅ Saved PURE changes only to: {pure_output} ({len(pure_df)} rows)")
