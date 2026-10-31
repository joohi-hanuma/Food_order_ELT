
# Food Orders Batch ELT Pipeline

Name : Akurati Joohi Hanuma 

## Project overview

This project implements the assigned batch-based ELT workflow with Python, Pandas, and MySQL. It reads `food_orders.csv` in batches of 100, preserves the original rows in a raw database, retrieves the raw records without changing that table, transforms and validates them with Pandas, and loads valid records into a separate analytics database.

The submitted run completed successfully: it extracted and loaded 1,010 source records in 11 batches, retrieved 1,010 raw records, transformed and loaded 1,000 valid records, and rejected 10 exact duplicate rows. All 11 analytics batches succeeded, no analytics batches failed, and final validation passed. These results are from the pipeline execution output shown for this dataset.

## Project files

```
Food_Orders_ELT_Submission/
├── food_orders.csv                 # Source dataset
├── food_orders_analysis.ipynb      # Pandas assignment analysis and validation
├── config.py                       # File, batch, and MySQL settings
├── extract.py                      # Read CSV as unchanged 100-row batches
├── load_raw.py                     # Create raw database/table; transactional inserts
├── retrieve_raw.py                 # Read raw records back in batches
├── transform.py                    # Deduplicate and transform with Pandas
├── validate.py                     # Validate rows and record rejection reasons
├── load_transformed.py             # Create analytics table; transactional batch inserts
├── elt_batch_pipeline.py           # Run the complete ELT workflow
├── business_analysis.sql           # Six required business-analysis queries
├── requirements.txt                # Python dependencies
├── .env.example                    # Safe MySQL configuration template
├── validation_report.json          # Pipeline validation report
├── rejected_records.csv            # Rejected rows and reasons after a pipeline run
└── transformed_valid_records.csv   # Valid transformed rows after a pipeline run
```

The two CSV outputs and `validation_report.json` are generated or refreshed by running the pipeline. Include the report and rejected-record file produced by your own successful run in the final submission.

## Databases and tables

The pipeline creates these databases and tables if they do not already exist:

| Database | Table | Purpose |
| --- | --- | --- |
| `food_orders_raw_db` | `raw_food_orders` | Stores the original CSV field values, including missing values and duplicate rows. |
| `food_orders_analytics_db` | `cleaned_food_orders` | Stores validated, typed records and the derived delivery-time and platform-revenue fields. |

The raw table adds an auto-increment `ingestion_id` for stable retrieval order. It is database metadata, not a source CSV column. Each write batch is inserted inside a transaction, so a failed batch is rolled back and reported.

## Transformation and validation rules

- Extraction reads the CSV in batches of 100 and does not clean or convert the source values before raw loading.

- Exact duplicates are identified by comparing every original source field. A shared fingerprint set is used across retrieved batches, so an exact duplicate split across batch boundaries is still detected. A repeated `Order ID` alone is not enough to delete a row.

- Timestamp strings are parsed into datetime values. Missing or invalid timestamps and negative delivery durations are rejected from the analytics table and recorded with rejection reasons.

- Financial fields are converted to numeric values when possible. Missing financial components remain missing rather than being replaced by zero.

- Missing payment methods are labeled `Unknown`; missing offer descriptions are labeled `Not Specified`.

- `Delivery_Time_Minutes` is calculated as delivery timestamp minus order timestamp, in minutes.

- `Platform_Net_Revenue` is calculated as Commission Fee + Delivery Fee − Payment Processing Fee − Refunds/Chargebacks. The result is left missing unless all four input values are present.

- Durations over 180 minutes are not automatically rejected. The notebook treats this as a review flag only.

## Requirements

- Windows 10/11, macOS, or Linux

- Python 3.10 or newer

- MySQL Server running locally or at a reachable host

- A MySQL account allowed to create databases and tables and to select and insert records

## Windows setup and configuration

Open PowerShell in the project folder. Create a virtual environment and install the dependencies:

```
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks environment activation, run this command for the current terminal session, then activate again:

```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Open `.env` in a text editor and enter the connection details for your MySQL server. For example:

```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
BATCH_SIZE=100
```

Do not commit `.env` or share the MySQL password. The `.gitignore` file excludes `.env` from Git. Keep `food_orders.csv` in this project folder unless you change `CSV_FILE` in `.env` to its full path.

## Run the analysis notebook

Open `food_orders_analysis.ipynb` in JupyterLab, Jupyter Notebook, or Visual Studio Code, select the project’s `.venv` Python environment, and choose **Run All**. Keep `food_orders.csv` in the same folder as the notebook. The notebook addresses the data-understanding, cleaning, transformation, business-question, visualization, and validation tasks.

## Run the ELT pipeline

Start MySQL, make sure `.env` contains the correct credentials, then run this command from the project folder:

```
python elt_batch_pipeline.py
```

The pipeline prints progress for each CSV extraction batch, raw-load batch, raw-read batch, and analytics-load batch. It writes or refreshes:

- `validation_report.json` — execution counts, validation checks, and final status

- `rejected_records.csv` — rejected records with rejection reasons

- `transformed_valid_records.csv` — valid transformed rows

### Results from the completed run

| Execution result | Count / status |
| --- | --- |
| Records extracted from CSV | 1,010 |
| Source batches processed | 11 |
| Raw records loaded | 1,010 |
| Raw records retrieved | 1,010 |
| Valid records transformed | 1,000 |
| Rejected records | 10 |
| Transformed records loaded | 1,000 |
| Successful analytics batches | 11 |
| Failed analytics batches | 0 |
| Final validation status | PASS |

The 10 rejections in the provided run were exact duplicate source rows. Check your own `validation_report.json` and `rejected_records.csv` after execution; actual counts depend on the source file and database contents.

## Run the SQL business analysis

After a successful pipeline run, open `business_analysis.sql` in MySQL Workbench or another MySQL client and execute it. The queries use `food_orders_analytics_db.cleaned_food_orders` to return:

1. Total order value.

1. Average order value.

1. Payment method with the most orders.

1. Order channel with the most orders.

1. Average valid delivery time in minutes.

1. Total platform net revenue.

The queries use available non-NULL values. Missing financial values are not silently treated as zero.

## Important: avoid accidental duplicate loads

The loaders append rows; they do not overwrite earlier batches. Running the pipeline again against the same populated databases loads the CSV again and changes the database counts. For a clean repeat run, use fresh empty databases/tables. Do not drop or truncate tables unless you are certain their contents can be deleted.

## Submit the project to GitHub

After adding the project files to your GitHub repository, include the successful run's `validation_report.json` and `rejected_records.csv`. Never add `.env`. To publish updated README or report files from an already connected local repository, run:

```
git status
git add README.md validation_report.json rejected_records.csv
git commit -m "Update project documentation and pipeline report"
git push
```

If Git says there is nothing to commit, the files are already up to date. Open the GitHub repository in your browser after pushing and verify that the README and generated report appear correctly.

