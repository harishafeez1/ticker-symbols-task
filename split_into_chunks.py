import os
import pandas as pd

# Config
INPUT_FILE = "filtered_ticker_changes.csv"
CHUNKS_DIR = "chunks"
CHUNK_SIZE = 500  # rows per chunk

# Create output folder
os.makedirs(CHUNKS_DIR, exist_ok=True)

# Load input
df = pd.read_csv(INPUT_FILE)

# Split and save
for i in range(0, len(df), CHUNK_SIZE):
    chunk_df = df.iloc[i:i+CHUNK_SIZE]
    chunk_index = i // CHUNK_SIZE + 1
    chunk_name = f"chunk_{chunk_index:03d}.csv"
    chunk_path = os.path.join(CHUNKS_DIR, chunk_name)
    chunk_df.to_csv(chunk_path, index=False)
    print(f"✅ Saved {chunk_name} with {len(chunk_df)} rows")

print(f"📦 Done. Created {chunk_index} chunks in '{CHUNKS_DIR}/'")
