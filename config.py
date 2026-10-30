"""Shared configuration for the food-orders batch ELT pipeline."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = Path(os.getenv("CSV_FILE", BASE_DIR / "food_orders.csv"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "port": int(os.getenv("MYSQL_PORT", "330")),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "Juhisonu@3"),
}
RAW_DB = "food_orders_raw_db"
RAW_TABLE = "raw_food_orders"
ANALYTICS_DB = "food_orders_analytics_db"
ANALYTICS_TABLE = "cleaned_food_orders"
REPORT_FILE = BASE_DIR / "validation_report.json"
REJECTED_FILE = BASE_DIR / "rejected_records.csv"
SOURCE_COLUMNS = [
    "Order ID", "Customer ID", "Restaurant ID", "Order Date and Time",
    "Delivery Date and Time", "Order Value", "Delivery Fee", "Payment Method",
    "Discounts and Offers", "Commission Fee", "Payment Processing Fee",
    "Refunds/Chargebacks", "Weather Condition", "Order Channel"
]
DATETIME_COLUMNS = ["Order Date and Time", "Delivery Date and Time"]
FINANCIAL_COLUMNS = [
    "Order Value", "Delivery Fee", "Commission Fee",
    "Payment Processing Fee", "Refunds/Chargebacks"
]
