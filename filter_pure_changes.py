import pandas as pd

# Load your full results file
df = pd.read_csv("occ_classified_results.csv")

# Keep only pure changes
pure_df = df[df['Classification'] == 'Pure'].copy()

# Optional: drop helper columns if not needed
output = pure_df[['Old Ticker', 'New Ticker', 'Effective Date', 'Post Date']]

# Save to final output
output.to_csv("validated_pure_ticker_changes.csv", index=False)

print(f"✅ Done. Kept {len(output)} pure ticker changes. Saved to validated_pure_ticker_changes.csv")
