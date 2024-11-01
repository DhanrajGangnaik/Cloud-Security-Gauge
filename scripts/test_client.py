import cx_Oracle

try:
    # Initialize Oracle Client explicitly with the path to Instant Client
    cx_Oracle.init_oracle_client(lib_dir=r"C:\PROJECTFOLDER\instantclient_23_5")   
    print("Oracle Client initialized successfully!")
except cx_Oracle.DatabaseError as e:
    error, = e.args
    print(f"Oracle Client initialization error: {error.message}")
