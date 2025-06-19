import os
import glob
import pandas as pd

CHUNKS_DIR = "chunks"
OUTPUT_DIR = "output"
ERRORS_DIR = "errors"

chunk_files = sorted(glob.glob(os.path.join(CHUNKS_DIR, "chunk_*.csv")))
output_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "output_*.csv")))
error_files = sorted(glob.glob(os.path.join(ERRORS_DIR, "errors_*.csv")))

total_chunks = len(chunk_files)
done_chunks = len(output_files)
pending_chunks = total_chunks - done_chunks

total_rows = 0
processed_rows = 0
error_rows = 0

for f in chunk_files:
    total_rows += pd.read_csv(f).shape[0]

for f in output_files:
    processed_rows += pd.read_csv(f).shape[0]

for f in error_files:
    error_rows += pd.read_csv(f).shape[0]

print(f"📊 Ticker Scraping Progress Summary")
print("-" * 40)
print(f"Total Chunks     : {total_chunks}")
print(f"Completed Chunks : {done_chunks}")
print(f"Pending Chunks   : {pending_chunks}")
print()
print(f"Total Rows       : {total_rows}")
print(f"Processed Rows   : {processed_rows}")
print(f"Error Rows       : {error_rows}")
print("-" * 40)

# Optionally, list pending chunk filenames
if pending_chunks > 0:
    pending = [f for f in chunk_files if not os.path.exists(os.path.join(OUTPUT_DIR, f"output_{f.split('_')[-1]}"))]
    print("🕒 Pending chunks:")
    for f in pending:
        print(" -", os.path.basename(f))
