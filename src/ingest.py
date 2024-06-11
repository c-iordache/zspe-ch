import sqlite3
import argparse
import os
import sys
import pandas as pd

def ingest_csv_real_estate_data_to_db(csv_path, db_path):
    # Check if the input CSV file exists
    if not os.path.isfile(csv_path):
        print(f"Error: The input CSV file '{csv_path}' does not exist.")
        sys.exit(1)

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading the CSV file '{csv_path}': {e}")
        sys.exit(1)
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"Error connecting to the SQLite database '{db_path}': {e}")
        sys.exit(1)
    
    try:
        # Write the DataFrame to the SQLite database
        df.to_sql('listings', conn, if_exists='replace', index=False)
    except Exception as e:
        print(f"Error writing to the SQLite database '{db_path}': {e}")
        sys.exit(1)
    finally:
        # Close the database connection
        conn.close()
        print(f"Data successfully ingested from '{csv_path}' to '{db_path}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ingest real estate property data from CSV into a SQLite database.')
    parser.add_argument('--db', type=str, default='../data/properties_db.db', help='Path to the SQLite database file.')
    parser.add_argument('--input', type=str, default='../data/zoomprop_data_engineering.csv', help='Path to the input CSV file.')
    args = parser.parse_args()

    ingest_csv_real_estate_data_to_db(args.input, args.db)
