import pandas as pd
import re

# Input and output files
INPUT_FILE = "pure_ticker_changes_step2.csv"
OUTPUT_FILE = "step2_final_pure_only.csv"

# Load input
df = pd.read_csv(INPUT_FILE)

# Classification function (based on OCC criteria)
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

# Apply classification
df["Classification"] = df["title"].apply(classify_memo)

# Filter only pure entries
pure_df = df[df["Classification"] == "Pure"]

# Save output
pure_df.to_csv(OUTPUT_FILE, index=False)
print(f"✅ Saved {len(pure_df)} pure entries to {OUTPUT_FILE}")
