"""Create the raw database and append original CSV batches transactionally."""
import mysql.connector
from config import MYSQL_CONFIG, RAW_DB, RAW_TABLE, SOURCE_COLUMNS
from db_utils import connect, quote_identifier
from extract import extract_batches


def create_raw_table():
    # Create the database first, then connect to it.
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {quote_identifier(RAW_DB)}")
    conn.commit()
    cur.close()
    conn.close()

    conn = connect(RAW_DB)
    cur = conn.cursor()
    # TEXT columns preserve the CSV's original text representation. NULLs and
    # duplicate source rows are allowed; ingestion_id uniquely identifies a row.
    columns_sql = ", ".join(f"{quote_identifier(c)} LONGTEXT NULL" for c in SOURCE_COLUMNS)
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS {quote_identifier(RAW_TABLE)} "
        f"(ingestion_id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, {columns_sql})"
    )
    conn.commit()
    cur.close()
    conn.close()


def load_raw_batches():
    create_raw_table()
    total = batches = successful = failed = 0
    conn = connect(RAW_DB)
    cur = conn.cursor()
    cols = ", ".join(quote_identifier(c) for c in SOURCE_COLUMNS)
    placeholders = ", ".join(["%s"] * len(SOURCE_COLUMNS))
    sql = f"INSERT INTO {quote_identifier(RAW_TABLE)} ({cols}) VALUES ({placeholders})"
    try:
        for batch_no, batch in extract_batches():
            rows = [tuple(None if value is None or str(value) == "nan" else str(value)
                          for value in row)
                    for row in batch[SOURCE_COLUMNS].itertuples(index=False, name=None)]
            try:
                cur.executemany(sql, rows)
                conn.commit()
                total += len(rows)
                successful += 1
                print(f"[RAW LOAD] Batch {batch_no} committed: {len(rows)} records")
            except Exception as exc:
                conn.rollback()
                failed += 1
                print(f"[RAW LOAD] Batch {batch_no} failed and was rolled back: {exc}")
                raise RuntimeError(f"Raw database batch {batch_no} failed") from exc
            batches += 1
    finally:
        cur.close()
        conn.close()

    conn = connect(RAW_DB)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {quote_identifier(RAW_TABLE)}")
    table_count = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"[RAW LOAD] Current total rows in raw table: {table_count}")
    return {"extracted": total, "extract_batches": batches,
            "raw_loaded_this_run": total, "raw_table_total": table_count,
            "raw_successful_batches": successful, "raw_failed_batches": failed}
