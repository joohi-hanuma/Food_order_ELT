"""Pandas transformations with exact-duplicate detection across all batches."""
import hashlib
import json
import pandas as pd
from config import SOURCE_COLUMNS, DATETIME_COLUMNS, FINANCIAL_COLUMNS


def row_fingerprint(row):
    """Create a stable fingerprint from original source values only."""
    values = [None if pd.isna(v) else str(v) for v in row]
    raw = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def transform_batch(raw_batch, seen_fingerprints):
    """Return (transformed_df, duplicate_rejections, duplicate_count)."""
    df = raw_batch[SOURCE_COLUMNS].copy()
    keep_indices = []
    duplicate_rows = []

    # The same set is passed to every batch, so duplicates across batches are caught.
    for index, row in df.iterrows():
        fingerprint = row_fingerprint(row.tolist())
        if fingerprint in seen_fingerprints:
            rejected = row.to_dict()
            rejected["Rejection_Reason"] = "EXACT_DUPLICATE_SOURCE_ROW"
            duplicate_rows.append(rejected)
        else:
            seen_fingerprints.add(fingerprint)
            keep_indices.append(index)

    df = df.loc[keep_indices].copy()
    duplicate_rejections = pd.DataFrame(duplicate_rows)

    # Convert timestamps; unparseable values become NaT and are rejected later.
    for col in DATETIME_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Convert financial values; invalid text becomes NaN and remains visible as missing.
    for col in FINANCIAL_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Delivery_Time_Minutes"] = (
        df["Delivery Date and Time"] - df["Order Date and Time"]
    ).dt.total_seconds() / 60

    revenue_inputs = ["Commission Fee", "Delivery Fee",
                      "Payment Processing Fee", "Refunds/Chargebacks"]
    df["Platform_Net_Revenue"] = (
        df["Commission Fee"] + df["Delivery Fee"]
        - df["Payment Processing Fee"] - df["Refunds/Chargebacks"]
    ).where(df[revenue_inputs].notna().all(axis=1))

    return df, duplicate_rejections, len(duplicate_rows)
