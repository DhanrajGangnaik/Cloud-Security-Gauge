import cx_Oracle # type: ignore

# Initialize the Oracle Client from the project folder
cx_Oracle.init_oracle_client(lib_dir=r"C:\PROJECTFOLDER\instantclient_23_5")

print("Oracle Client initialized successfully")