"""Run the full batch-based ELT pipeline."""
import json
import pandas as pd
from config import REPORT_FILE, REJECTED_FILE, BATCH_SIZE, SOURCE_COLUMNS
from load_raw import load_raw_batches
from retrieve_raw import retrieve_raw_batches
from transform import transform_batch
from validate import validate_batch, validation_summary
from load_transformed import create_analytics_table, load_analytics_batch, analytics_table_count


def main():
    print("========== FOOD ORDERS ELT PIPELINE ==========")
    raw_stats = load_raw_batches()
    create_analytics_table()

    seen_fingerprints = set()
    all_valid = []
    all_rejected = []
    duplicate_count = 0
    retrieved_count = 0
    analytics_success = 0
    analytics_failed = 0
    transformed_batches = 0

    # A shared fingerprint set catches exact duplicates across batch boundaries.
    for batch_no, raw_batch in retrieve_raw_batches():
        retrieved_count += len(raw_batch)
        transformed, duplicate_rejections, duplicates = transform_batch(raw_batch, seen_fingerprints)
        duplicate_count += duplicates
        if not duplicate_rejections.empty:
            all_rejected.append(duplicate_rejections)

        valid, rejected = validate_batch(transformed)
        if not rejected.empty:
            all_rejected.append(rejected)
        all_valid.append(valid)
        transformed_batches += 1

        try:
            load_analytics_batch(valid, batch_no)
            analytics_success += 1
        except Exception:
            analytics_failed += 1
            raise

    valid_df = pd.concat(all_valid, ignore_index=True) if all_valid else pd.DataFrame()
    rejected_df = pd.concat(all_rejected, ignore_index=True, sort=False) if all_rejected else pd.DataFrame()
    valid_df.to_csv("transformed_valid_records.csv", index=False)
    rejected_df.to_csv(REJECTED_FILE, index=False)

    report = validation_summary(valid_df, rejected_df, duplicate_count)
    report.update({
        "source_file": "food_orders.csv",
        "batch_size": BATCH_SIZE,
        "total_records_extracted_this_run": raw_stats["extracted"],
        "total_source_batches": raw_stats["extract_batches"],
        "raw_records_loaded_this_run": raw_stats["raw_loaded_this_run"],
        "raw_table_total_after_load": raw_stats["raw_table_total"],
        "total_raw_records_retrieved": retrieved_count,
        "total_valid_records_transformed": int(len(valid_df)),
        "total_rejected_records_including_duplicates": int(len(rejected_df)),
        "total_transformed_records_loaded_this_run": int(len(valid_df)),
        "analytics_table_total_after_load": int(analytics_table_count()),
        "raw_successful_batches": raw_stats["raw_successful_batches"],
        "raw_failed_batches": raw_stats["raw_failed_batches"],
        "analytics_successful_batches": analytics_success,
        "analytics_failed_batches": analytics_failed,
        "transformation_decisions": {
            "duplicates": "Exact duplicate source rows are removed using a SHA-256 fingerprint of all original columns across all batches.",
            "missing_values": "Unknown values are not replaced with zero. Revenue remains NULL when any required revenue component is missing.",
            "invalid_records": "Missing/unparseable order or delivery timestamps and negative delivery durations are rejected with reasons.",
            "long_deliveries": "Durations over 180 minutes are retained but can be reviewed separately; this is not used as an automatic rejection rule."
        }
    })
    REPORT_FILE.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")

    print("\n========== FINAL EXECUTION REPORT ==========")
    print(f"Total records extracted from CSV: {report['total_records_extracted_this_run']}")
    print(f"Total source batches processed: {report['total_source_batches']}")
    print(f"Raw records loaded this run: {report['raw_records_loaded_this_run']}")
    print(f"Total raw records retrieved: {report['total_raw_records_retrieved']}")
    print(f"Total valid records transformed: {report['total_valid_records_transformed']}")
    print(f"Total rejected records: {report['total_rejected_records_including_duplicates']}")
    print(f"Transformed records loaded this run: {report['total_transformed_records_loaded_this_run']}")
    print(f"Successful analytics batches: {report['analytics_successful_batches']}")
    print(f"Failed analytics batches: {report['analytics_failed_batches']}")
    print(f"Final validation status: {report['validation_status']}")
    print(f"Validation report: {REPORT_FILE}")
    print("============================================")


if __name__ == "__main__":
    main()
