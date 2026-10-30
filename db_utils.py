"""Small MySQL helpers shared by pipeline stages."""
import mysql.connector
from config import MYSQL_CONFIG


def connect(database=None):
    settings = dict(MYSQL_CONFIG)
    if database:
        settings["database"] = database
    return mysql.connector.connect(**settings)


def quote_identifier(name):
    """Quote a trusted identifier such as a column or database name."""
    return "`" + name.replace("`", "``") + "`"
