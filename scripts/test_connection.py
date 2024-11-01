import cx_Oracle

# Initialize Oracle Client explicitly
cx_Oracle.init_oracle_client(lib_dir=r"C:\PROJECTFOLDER\instantclient_23_5")  # Replace with actual path to Instant Client

# Test connection
dsn = "localhost:1521/XE"
username = "system"
password = "oracle"

try:
    connection = cx_Oracle.connect(username, password, dsn)
    print("Connection successful!")
    connection.close()
except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"Database connection error: {error.message}")
