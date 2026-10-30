"""Create the analytics table and insert validated batches transactionally."""
import mysql.connector
import pandas as pd
from config import MYSQL_CONFIG, ANALYTICS_DB, ANALYTICS_TABLE, SOURCE_COLUMNS
from db_utils import connect, quote_identifier


def create_analytics_table():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {quote_identifier(ANALYTICS_DB)}")
    conn.commit()
    cur.close()
    conn.close()

    conn = connect(ANALYTICS_DB)
    cur = conn.cursor()
    columns = []
    for col in SOURCE_COLUMNS:
        if col in ["Order Date and Time", "Delivery Date and Time"]:
            sql_type = "DATETIME NULL"
        elif col in ["Order Value", "Delivery Fee", "Commission Fee", "Payment Processing Fee", "Refunds/Chargebacks"]:
            sql_type = "DECIMAL(14,2) NULL"
        else:
            sql_type = "VARCHAR(255) NULL"
        columns.append(f"{quote_identifier(col)} {sql_type}")
    columns.extend([
        "`Delivery_Time_Minutes` DECIMAL(12,2) NULL",
        "`Platform_Net_Revenue` DECIMAL(14,2) NULL"
    ])
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS {quote_identifier(ANALYTICS_TABLE)} "
        f"(`analytics_id` BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY, {', '.join(columns)})"
    )
    conn.commit()
    cur.close()
    conn.close()


def _mysql_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if hasattr(value, "item"):
        value = value.item()
    return value


def load_analytics_batch(df, batch_no):
    if df.empty:
        return 0
    columns = SOURCE_COLUMNS + ["Delivery_Time_Minutes", "Platform_Net_Revenue"]
    conn = connect(ANALYTICS_DB)
    cur = conn.cursor()
    col_sql = ", ".join(quote_identifier(c) for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO {quote_identifier(ANALYTICS_TABLE)} ({col_sql}) VALUES ({placeholders})"
    rows = [tuple(_mysql_value(v) for v in row)
            for row in df[columns].itertuples(index=False, name=None)]
    try:
        cur.executemany(sql, rows)
        conn.commit()
        print(f"[ANALYTICS LOAD] Batch {batch_no} committed: {len(rows)} records")
        return len(rows)
    except Exception as exc:
        conn.rollback()
        print(f"[ANALYTICS LOAD] Batch {batch_no} rolled back: {exc}")
        raise RuntimeError(f"Analytics database batch {batch_no} failed") from exc
    finally:
        cur.close()
        conn.close()


def analytics_table_count():
    conn = connect(ANALYTICS_DB)
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {quote_identifier(ANALYTICS_TABLE)}")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count
