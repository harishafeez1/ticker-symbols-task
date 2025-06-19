import pandas as pd
import re

# Load the original CSV
input_file = "ticker_data_fixed.csv"  # Update path if needed
output_file = "filtered_ticker_changes.csv"

# Load the CSV
df = pd.read_csv(input_file)

# Normalize column names (in case of weird spacing)
df.columns = [col.strip() for col in df.columns]

# Function to determine if ticker is a pure change
def is_pure_ticker(ticker):
    """
    Returns True if the ticker looks pure (no numeric suffix or Q flags).
    """
    # Reject tickers ending with numbers, 'Q', or 'W' (e.g., ABC1, MEHCQ, DEF1W)
    return not bool(re.search(r'\d|Q$|W$', ticker.upper()))

# Apply the filter
df['IsPureChange'] = df['New Ticker'].apply(is_pure_ticker)

# Keep only pure ticker changes
pure_df = df[df['IsPureChange']].copy()

# Save filtered results
pure_df.to_csv(output_file, index=False)

print(f"Filtered dataset saved to {output_file}")
print(f"Original rows: {len(df)}, After filtering: {len(pure_df)}")
