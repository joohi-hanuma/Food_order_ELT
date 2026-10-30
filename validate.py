"""Validate transformed batches and separate rejected records with reasons."""
import pandas as pd
from config import SOURCE_COLUMNS, DATETIME_COLUMNS, FINANCIAL_COLUMNS


def validate_batch(df):
    """Return valid records and rejected records, each rejection with a reason."""
    df = df.copy()
    reasons = [[] for _ in range(len(df))]

    # Require usable timestamps to calculate a delivery duration.
    for pos, (_, row) in enumerate(df.iterrows()):
        if pd.isna(row["Order Date and Time"]):
            reasons[pos].append("INVALID_OR_MISSING_ORDER_TIMESTAMP")
        if pd.isna(row["Delivery Date and Time"]):
            reasons[pos].append("INVALID_OR_MISSING_DELIVERY_TIMESTAMP")
        duration = row["Delivery_Time_Minutes"]
        if pd.notna(duration) and duration < 0:
            reasons[pos].append("NEGATIVE_DELIVERY_DURATION")

    reason_text = [";".join(items) for items in reasons]
    rejected_mask = pd.Series([bool(items) for items in reasons], index=df.index)
    rejected = df.loc[rejected_mask].copy()
    rejected["Rejection_Reason"] = [reason_text[i] for i, flag in enumerate(rejected_mask.tolist()) if flag]
    valid = df.loc[~rejected_mask].copy()

    # Check the revenue formula for rows where all four inputs are present.
    revenue_cols = ["Commission Fee", "Delivery Fee", "Payment Processing Fee", "Refunds/Chargebacks"]
    complete = valid[revenue_cols].notna().all(axis=1)
    expected = (valid["Commission Fee"] + valid["Delivery Fee"]
                - valid["Payment Processing Fee"] - valid["Refunds/Chargebacks"])
    if complete.any() and not ((valid.loc[complete, "Platform_Net_Revenue"] - expected.loc[complete]).abs() < 1e-8).all():
        raise ValueError("Platform net revenue validation failed")

    # Verify duration calculation for every valid row with timestamps.
    expected_duration = (valid["Delivery Date and Time"] - valid["Order Date and Time"]).dt.total_seconds() / 60
    if not (valid["Delivery_Time_Minutes"].sub(expected_duration).abs().fillna(0) < 1e-8).all():
        raise ValueError("Delivery duration validation failed")

    return valid, rejected


def validation_summary(valid_df, rejected_df, duplicate_count):
    """Build a JSON-serializable validation summary."""
    return {
        "valid_records": int(len(valid_df)),
        "rejected_records_excluding_duplicates": int(len(rejected_df)),
        "exact_duplicates_removed": int(duplicate_count),
        "remaining_duplicate_rows": int(valid_df.duplicated(subset=SOURCE_COLUMNS).sum()),
        "missing_values_in_valid_records": {str(k): int(v) for k, v in valid_df.isna().sum().items()},
        "datetime_dtypes": {c: str(valid_df[c].dtype) for c in DATETIME_COLUMNS},
        "financial_dtypes": {c: str(valid_df[c].dtype) for c in FINANCIAL_COLUMNS},
        "delivery_duration_calculation": "PASS",
        "platform_net_revenue_calculation": "PASS",
        "validation_status": "PASS" if valid_df.duplicated(subset=SOURCE_COLUMNS).sum() == 0 else "FAIL"
    }
