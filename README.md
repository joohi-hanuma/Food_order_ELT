# Food Orders Batch ELT Project

**Name:** Akurati Joohi Hanuma
**Batch:** 1

This submission contains a Pandas analysis notebook and a separate batch-based ELT pipeline. The pipeline extracts the original CSV in batches of 100, loads unchanged source values to `food_orders_raw_db.raw_food_orders`, retrieves those values in batches, transforms and validates them with Pandas, and appends valid rows to `food_orders_analytics_db.cleaned_food_orders`.

## Project contents

- `food_orders_analysis.ipynb` — assignment Tasks 1–8: dataset understanding, quality assessment, documented cleaning, derived fields, business questions, charts, and validation.
- `food_orders.csv` — source file used by the notebook and ELT pipeline.
- `config.py` — batch size, source path, database names, and environment-based MySQL connection settings.
- `extract.py` — reads the CSV without transforming values and yields 100-row batches.
- `load_raw.py` — creates the raw database/table and commits each batch in a transaction.
- `retrieve_raw.py` — reads raw table rows in stable `ingestion_id` order and yields 100-row batches.
- `transform.py` — removes exact repeated source rows across all retrieved batches, parses timestamp and financial fields, and derives duration and net revenue.
- `validate.py` — separates invalid-timestamp and negative-duration records, checks derived calculations, and builds validation metrics.
- `load_transformed.py` — creates the analytics database/table and inserts valid records transactionally in batches.
- `elt_batch_pipeline.py` — coordinates the workflow and writes the runtime report and rejected-record CSV.
- `business_analysis.sql` — SQL answers for the six required analytics questions.
- `validation_report.json` — local CSV validation/preflight report. It is not a MySQL execution report; run the pipeline to generate the live report.
- `requirements.txt` and `.env.example` — dependencies and safe configuration template.

## Cleaning and business assumptions

The raw table preserves source values as text, along with source missing values and duplicate rows; the auto-increment `ingestion_id` is database metadata only. Exact duplicate records are detected from all original columns across batch boundaries. A repeated `Order ID` alone is not used to delete a row because the supplied dataset does not establish that ID repetition proves duplicate ingestion. In this CSV there are 20 rows associated with repeated Order IDs before removing exact duplicates; after the 10 exact repeated rows are removed, no repeated IDs remain.

Missing financial values remain missing. `Platform_Net_Revenue` is calculated only when Commission Fee, Delivery Fee, Payment Processing Fee, and Refunds/Chargebacks are all present. Missing payment methods are labeled `Unknown`; missing offer descriptions are labeled `Not Specified`. Missing or unparseable timestamps and negative delivery durations are rejected from the analytics table and their reasons are recorded in `rejected_records.csv`. Durations above 180 minutes are retained; 180 minutes is only a review threshold in the notebook, not an automatic rejection condition.

## Requirements and MySQL setup

Use Python 3.10 or newer and a running MySQL Server. Create a virtual environment, then install dependencies:

**macOS/Linux**

```bash
cd Food_Orders_ELT_Submission
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

**Windows PowerShell**

```powershell
cd Food_Orders_ELT_Submission
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Validation and report notes

The included `validation_report.json` records checks that can be performed directly from the supplied CSV without a live MySQL service. It explicitly says the MySQL-backed workflow was not executed in this prepared environment. After running `elt_batch_pipeline.py` on your computer, the pipeline replaces that report with counts from your database-backed run. Review the `validation_status`, record totals, rejected rows, and batch success/failure counts before submitting. The counts in the runtime report depend on your database state; use a fresh empty database for a clean, reproducible run.

