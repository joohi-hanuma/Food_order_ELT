"""Retrieve the raw table in stable, read-only batches."""
import pandas as pd
from config import RAW_DB, RAW_TABLE, BATCH_SIZE, SOURCE_COLUMNS
from db_utils import connect, quote_identifier


def retrieve_raw_batches():
    conn = connect(RAW_DB)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {quote_identifier(RAW_TABLE)}")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()

    offset = 0
    batch_no = 1
    while offset < total:
        conn = connect(RAW_DB)
        cur = conn.cursor(dictionary=True)
        cur.execute(
            f"SELECT * FROM {quote_identifier(RAW_TABLE)} "
            f"ORDER BY ingestion_id LIMIT %s OFFSET %s", (BATCH_SIZE, offset)
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        if not rows:
            break
        df = pd.DataFrame(rows)
        # ingestion_id is database metadata, not part of the original CSV.
        df = df[SOURCE_COLUMNS]
        print(f"[RAW READ] Batch {batch_no}: {len(df)} records retrieved")
        yield batch_no, df
        offset += len(rows)
        batch_no += 1
