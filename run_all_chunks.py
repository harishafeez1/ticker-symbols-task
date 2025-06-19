import os
import glob
import subprocess
import time
import pandas as pd

CHUNKS_DIR = "chunks"
OUTPUT_DIR = "output"
SCRIPT = "occ_scraper_chunked.py"
MAX_PARALLEL = 2

def chunk_id_from_path(path):
    return os.path.splitext(os.path.basename(path))[0].split("_")[-1]

def chunk_is_done(chunk_file):
    chunk_id = os.path.splitext(os.path.basename(chunk_file))[0].split("_")[-1]
    output_file = os.path.join(OUTPUT_DIR, f"output_{chunk_id}.csv")
    
    if not os.path.exists(output_file):
        return False

    # Compare row counts
    try:
        original_rows = pd.read_csv(chunk_file).shape[0]
        output_rows = pd.read_csv(output_file).shape[0]
        return output_rows >= original_rows  # Allow for over-processing, just in case
    except:
        return False  # If any error, treat as incomplete
    

def main():
    chunk_files = sorted(glob.glob(os.path.join(CHUNKS_DIR, "chunk_*.csv")))
    chunks_to_run = [c for c in chunk_files if not chunk_is_done(c)]

    print(f"🔍 Found {len(chunk_files)} chunks, {len(chunks_to_run)} pending")

    active = []
    queue = chunks_to_run[:]

    while queue or active:
        # Remove finished
        active = [p for p in active if p.poll() is None]

        # Launch new ones
        while len(active) < MAX_PARALLEL and queue:
            chunk_file = queue.pop(0)
            print(f"🟡 Launching: {chunk_file}")
            proc = subprocess.Popen(["python", SCRIPT, chunk_file])
            active.append(proc)

        time.sleep(3)

    print("✅ All chunks processed.")

if __name__ == "__main__":
    main()
