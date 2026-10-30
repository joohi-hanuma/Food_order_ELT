"""Read the source CSV in unchanged batches."""
import pandas as pd
from config import CSV_FILE, BATCH_SIZE


def extract_batches():
    """Yield raw DataFrames; no cleaning or type conversion is performed."""
    for batch_number, batch in enumerate(
        pd.read_csv(CSV_FILE, chunksize=BATCH_SIZE, dtype=str), start=1
    ):
        print(f"[EXTRACT] Batch {batch_number}: {len(batch)} records")
        yield batch_number, batch
