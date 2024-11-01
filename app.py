from flask import Flask, render_template, request, redirect, url_for, flash, session
import cx_Oracle
import csv
import os
import re

# Set up the Oracle Instant Client library path
cx_Oracle.init_oracle_client(lib_dir=r"C:\PROJECTFOLDER\instantclient_23_5")

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
dsn = "localhost:1521/XE"
username = "system"
password = "oracle"

# Initialize a connection pool
pool = cx_Oracle.SessionPool(
    user=username,
    password=password,
    dsn=dsn,
    min=2,
    max=10,
    increment=1,
    threaded=True
)

# Input validation functions
def is_valid_username(username):
    return re.match("^[a-zA-Z0-9_]{3,30}$", username)

def is_valid_password(password):
    return 8 <= len(password) <= 30

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        
        # Input validation
        if not is_valid_username(user) or not is_valid_password(pw):
            flash("Invalid username or password format.", "danger")
            return redirect(url_for('login'))
        
        try:
            # Get a connection from the pool
            connection = pool.acquire()
            cursor = connection.cursor()
            
            # Fetch the user's password from the database
            cursor.execute(
                "SELECT password FROM users WHERE username = :username",
                {"username": user}
            )
            result = cursor.fetchone()
            
            # Debugging output for each step
            if result:
                stored_password = result[0]
                print(f"DEBUG: Retrieved password from database: {stored_password}")
                print(f"DEBUG: Password entered by user: {pw}")
                
                # Check if stored password matches entered password
                if stored_password == pw:  # For plain text comparison during testing
                    print("DEBUG: Passwords match. Logging in user.")
                    session['username'] = user
                    flash("Login successful!", "success")
                    return redirect(url_for('home'))
                else:
                    print("DEBUG: Passwords do not match.")
                    flash("Invalid password.", "danger")
            else:
                print("DEBUG: No user found with that username.")
                flash("Invalid username.", "danger")
        
        except cx_Oracle.DatabaseError as e:
            print(f"Database error: {e}")
            flash(f"Database error: {str(e)}", "danger")
        
        finally:
            # Release the connection back to the pool
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                pool.release(connection)

    return render_template('login.html')


@app.route('/home')
def home():
    if 'username' not in session:
        flash("Please log in first", "warning")
        return redirect(url_for('login'))
    
    try:
        connection = pool.acquire()
        cursor = connection.cursor()
        
        # Fetch data with limited rows to prevent data overload
        cursor.execute("SELECT transaction_id, transaction_date, amount, category, is_fraud FROM credit_card_fraud FETCH FIRST 100 ROWS ONLY")
        result = cursor.fetchall()
        
        if result:
            flash("Data fetched successfully!", "info")
        else:
            flash("No data available in the table.", "warning")

        return render_template('home.html', table=result)
    
    except cx_Oracle.DatabaseError as e:
        flash("Failed to fetch data from the database.", "danger")
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            pool.release(connection)

@app.route('/load_data')
def load_data():
    if 'username' not in session:
        flash("Please log in first", "warning")
        return redirect(url_for('login'))

    # Path to the CSV file in the container or local directory
    csv_file_path = "data/credit_card_fraud_dataset.csv"  # Adjust path if necessary

    try:
        connection = pool.acquire()
        cursor = connection.cursor()
        
        # Open and read the CSV file
        with open(csv_file_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip the header row

            # Insert each row securely
            for row in csv_reader:
                cursor.execute("""
                    INSERT INTO credit_card_fraud (transaction_id, transaction_date, amount, category, is_fraud)
                    VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5)
                """, row)

        # Commit the transaction
        connection.commit()
        flash("Data loaded successfully from CSV!", "success")
    
    except FileNotFoundError:
        flash("CSV file not found. Please ensure the file is available.", "danger")
    
    except cx_Oracle.DatabaseError as e:
        flash(f"Database error: {str(e)}", "danger")
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            pool.release(connection)

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))

# Security headers to prevent XSS, clickjacking, etc.
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

if __name__ == '__main__':
    app.run(debug=True)
