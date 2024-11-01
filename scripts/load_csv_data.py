import os
import cx_Oracle
import csv
from datetime import datetime

# Add Instant Client path to PATH
cx_Oracle.init_oracle_client(lib_dir=r"C:\PROJECTFOLDER\instantclient_23_5")

# Add Instant Client path and initialize the client
os.environ["PATH"] = r"C:\PROJECTFOLDER\instantclient_23_5" + ";" + os.environ["PATH"]
cx_Oracle.init_oracle_client(lib_dir=r"C:\PROJECTFOLDER\instantclient_23_5")

# Establish a connection to the Oracle database
connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)

# Path to the CSV file
csv_file_path = os.path.join(os.getcwd(), "credit_card_fraud_dataset.csv")

# Database connection settings
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="XE")
username = "system"  # Replace with actual username
password = "oracle"  # Replace with actual password


# Establish a connection to the Oracle database
connection = cx_Oracle.connect(user=username, password=password, dsn=dsn)
cursor = connection.cursor()

# Step 1: Create the table if it does not already exist
table_creation_query = """
CREATE TABLE credit_card_fraud (
    transaction_id NUMBER,
    transaction_date DATE,
    amount NUMBER,
    category VARCHAR2(50),
    is_fraud CHAR(1)
)
"""

try:
    cursor.execute(table_creation_query)
    print("Table 'credit_card_fraud' created successfully.")
except cx_Oracle.DatabaseError as e:
    error, = e.args
    if "ORA-00955" in error.message:
        print("Table 'credit_card_fraud' already exists. Skipping creation.")
    else:
        print(f"Error creating table: {error.message}")

# Step 2: Load data from the CSV file
try:
    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip header row

        for row in csv_reader:
            # Convert date format if necessary (assuming format 'YYYY-MM-DD' in CSV)
            transaction_date = datetime.strptime(row[1], "%Y-%m-%d") if row[1] else None
            
            # Insert data into the table
            cursor.execute("""
                INSERT INTO credit_card_fraud (transaction_id, transaction_date, amount, category, is_fraud)
                VALUES (:1, :2, :3, :4, :5)
            """, (int(row[0]), transaction_date, float(row[2]), row[3], row[4]))

    # Commit the transaction
    connection.commit()
    print("CSV data loaded successfully into 'credit_card_fraud' table.")

except Exception as e:
    print(f"Error loading data: {e}")

finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
