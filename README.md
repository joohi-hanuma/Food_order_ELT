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

Edit `.env` with your local MySQL values. For example:

```text
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_local_mysql_password
# CSV_FILE=/absolute/path/to/food_orders.csv
BATCH_SIZE=100
```

Do not commit `.env` or share your database password. The Python code creates the two databases and tables if they do not exist; the MySQL account needs permission to create databases and tables and insert/select data.

## Run the notebook

Open `food_orders_analysis.ipynb` in Jupyter Notebook, JupyterLab, or VS Code with the project environment selected. Run all cells from top to bottom. Keep `food_orders.csv` beside the notebook, or adjust `CSV_PATH` in its first code cell.

## Run the complete ELT workflow

From the project directory with the virtual environment active and MySQL running:

```bash
python elt_batch_pipeline.py
```

The run prints batch progress and a final execution summary. It writes `validation_report.json`, `rejected_records.csv`, and `transformed_valid_records.csv` in this folder. The pipeline appends batches; a rerun against the same databases will ingest source rows again. For a fresh assignment run, use empty databases/tables. If you choose to clear tables, make sure you are not deleting data you need to preserve.

## Run the SQL analysis

After the pipeline completes, open `business_analysis.sql` in MySQL Workbench or another MySQL client. Execute the statements against `food_orders_analytics_db`. Totals and averages use non-NULL values in the analytics table; missing values are not silently converted to zero.

## Validation and report notes

The included `validation_report.json` records checks that can be performed directly from the supplied CSV without a live MySQL service. It explicitly says the MySQL-backed workflow was not executed in this prepared environment. After running `elt_batch_pipeline.py` on your computer, the pipeline replaces that report with counts from your database-backed run. Review the `validation_status`, record totals, rejected rows, and batch success/failure counts before submitting. The counts in the runtime report depend on your database state; use a fresh empty database for a clean, reproducible run.

## Publish your own GitHub repository

Create an **empty** repository under your own GitHub account (do not choose “Add a README” if you already have this folder's README). From a terminal, run these commands from the project directory. Replace `YOUR_GITHUB_USERNAME` and `YOUR_REPOSITORY_NAME` with your own values:

```bash
git init
git add README.md requirements.txt .gitignore .env.example *.py *.sql *.ipynb *.csv validation_report.json
git status
git commit -m "Submit food orders ELT pipeline and analysis"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git
git push -u origin main
```

Before committing, check `git status` and confirm that `.env` is not listed. If Git asks for authentication, sign in through the official GitHub flow or use a personal access token as GitHub prompts; never place a token in a file or share it. Your public repository link will be:

```text
https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME
```

## Message to your instructor

After pushing and checking that the repository opens in a private/incognito window, send:

> Hello Sir, I have completed the Food Orders Data Understanding and Batch ELT Pipeline assignment. The Jupyter notebook, Python pipeline, SQL analysis, source CSV, README, and validation report are available here: **[paste your GitHub repository link]**. Thank you.
