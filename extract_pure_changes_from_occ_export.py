import pandas as pd
import re
if __name__ == "__main__":
    # Load and process directly
    df = pd.read_csv("memo_export.csv")

    # Normalize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    def classify_memo(title):
        title = str(title).lower()
        if "symbol change" in title or "name/symbol change" in title:
            if any(term in title for term in ["reverse", "split", "merger", "adjustment", "consolidation", "cusip", "tender", "bankrupt"]):
                return "Adjustment"
            if re.search(r'new symbol:\s*[A-Z]+[1QW]', title, re.IGNORECASE):
                return "Adjustment"
            return "Pure"
        return "Irrelevant"

    df['classification'] = df['title'].apply(classify_memo)

    def extract_tickers(title):
        match = re.search(r'Option Symbol:\s*([A-Z]{2,6})\s+New Symbol:\s*([A-Z]{2,6})', title)
        if match:
            return pd.Series([match.group(1), match.group(2)])
        return pd.Series(["", ""])

    df[['old_ticker', 'new_ticker']] = df['title'].apply(extract_tickers)
    pure_df = df[df['classification'] == "Pure"].copy()
    pure_df = pure_df[pure_df['old_ticker'] != ""]

    pure_df[['old_ticker', 'new_ticker', 'ex/eff_date', 'post_date', 'title']].to_csv(
        "pure_ticker_changes_step2.csv", index=False
    )

    print(f"✅ Saved {len(pure_df)} pure ticker changes to 'pure_ticker_changes_step2.csv'")
