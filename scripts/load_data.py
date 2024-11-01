import cx_Oracle
import csv
import os
from datetime import datetime

# Set up the Oracle Instant Client library path
cx_Oracle.init_oracle_client(lib_dir=os.path.join("C:", "PROJECTFOLDER", "instantclient_23_5"))

# Database configuration
dsn = "localhost:1521/XE"
username = "system"
password = "oracle"  # Updated to the password you're using

# Path to the CSV file
csv_file_path = os.path.join("..", "data", "credit_card_fraud_dataset.csv")

# Helper function to parse the date and timestamp from CSV
def parse_date(date_string):
    date_formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%d-%m-%Y",
        "%m/%d/%Y"
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_string, fmt).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    raise ValueError(f"Date format for '{date_string}' is not recognized.")

# Helper function to parse the is_fraud column
def parse_is_fraud(value):
    if value.lower() in ['fraud', 'yes', 'y']:
        return 'Y'
    elif value.lower() in ['not fraud', 'no', 'n']:
        return 'N'
    else:
        return 'N'  # Default to 'N' if the value is not recognized

try:
    # Connect to the Oracle database
    connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
    cursor = connection.cursor()

    # Open and read the CSV file
    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header row

        row_count = 0  # Track successful row inserts

        # Insert each row into the database
        for row in csv_reader:
            try:
                # Parse the transaction_date with date and time handling
                transaction_date = parse_date(row[1])

                # Parse is_fraud to ensure it’s 'Y' or 'N'
                is_fraud = parse_is_fraud(row[4])

                cursor.execute("""
                    INSERT INTO credit_card_fraud (transaction_id, transaction_date, amount, category, is_fraud)
                    VALUES (:1, TO_TIMESTAMP(:2, 'YYYY-MM-DD HH24:MI:SS'), :3, :4, :5)
                """, (row[0], transaction_date, row[2], row[3], is_fraud))
                row_count += 1
            except ValueError as ve:
                print(f"Skipping row due to date format error: {ve}")
            except cx_Oracle.DatabaseError as e:
                print(f"Database error while inserting row: {e}")
        
        # Commit the transaction if there are rows to commit
        if row_count > 0:
            connection.commit()
            print(f"Data loaded successfully from CSV! {row_count} rows inserted.")
        else:
            print("No data was inserted due to errors in all rows.")
except FileNotFoundError:
    print("CSV file not found. Please ensure the file is available.")
except cx_Oracle.DatabaseError as e:
    print(f"Database error: {e}")
except cx_Oracle.InterfaceError as e:
    print(f"Oracle client connection error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()
