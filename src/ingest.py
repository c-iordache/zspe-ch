import sqlite3
#import argparse
import os
import sys
import logging
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read paths from environment variables
DATA_FILE_PATH = os.getenv('DATA_FILE_PATH')
DB_PATH = os.getenv('DB_PATH')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ingest_csv_real_estate_data_to_db(csv_path, db):
    """
    Ingests real estate data from a CSV file into a SQLite database.

    Parameters:
    csv_path (str): Path to the input CSV file.
    db (str or sqlite3.Connection): Path to the SQLite database file or an SQLite connection object.
    """
    # Check if the input CSV file exists
    if isinstance(csv_path, str) and not os.path.isfile(csv_path):
        logging.error("The input CSV file '%s' does not exist.", csv_path)
        raise FileNotFoundError(f"The input CSV file '{csv_path}' does not exist.")

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_path)
    except Exception as e:
        logging.error("Error reading the CSV file '%s': %s", csv_path, e)
        raise ValueError(f"Error reading the CSV file '{csv_path}': {e}")

    try:
        # Use provided connection or create a new one
        if isinstance(db, sqlite3.Connection):
            conn = db
        else:
            conn = sqlite3.connect(db)
    except sqlite3.Error as e:
        logging.error("Error connecting to the SQLite database '%s': %s", db, e)
        raise sqlite3.DatabaseError(f"Error connecting to the SQLite database '{db}': {e}")

    try:
        # Write the DataFrame to the SQLite database
        df.to_sql('listings', conn, if_exists='replace', index=False)
    except Exception as e:
        logging.error("Error writing to the SQLite database '%s': %s", db, e)
        raise sqlite3.DatabaseError(f"Error writing to the SQLite database '{db}': {e}")
    finally:
        if not isinstance(db, sqlite3.Connection):
            conn.close()
        logging.info("Data successfully ingested from '%s' to '%s'.", csv_path, db)
