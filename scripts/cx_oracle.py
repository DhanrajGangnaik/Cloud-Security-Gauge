import cx_Oracle

cx_Oracle.init_oracle_client(lib_dir=r"C:\PROJECTFOLDER\instantclient_23_5")

connection = cx_Oracle.connect(user="system", password="oracle", dsn="localhost:1521/XE")
cursor = connection.cursor()
cursor.execute("SELECT password FROM users WHERE username = :username", {"username": "test_user"})
result = cursor.fetchone()
print("Password from database:", result[0] if result else "User not found")
cursor.close()
connection.close()
