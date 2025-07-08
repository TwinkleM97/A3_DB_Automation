from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # required for sessions

def connect_db():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "student"),
            password=os.getenv("DB_PASS", "studentpass"),
            database=os.getenv("DB_NAME", "prog8850_db")
        )
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("register.html")
        
        conn = connect_db()
        if not conn:
            flash("Database connection failed.", "danger")
            return render_template("register.html")
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            if user:
                flash("Username already exists.", "danger")
                return render_template("register.html")
            
            # Store plaintext password — for demo purposes only
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash("Registered successfully. Please login.", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
            return render_template("register.html")
        finally:
            conn.close()
    
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html")
        
        conn = connect_db()
        if not conn:
            flash("Database connection failed.", "danger")
            return render_template("login.html")
        
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            
            # Compare directly — because password is in plain text
            if user and user['password'] == password:
                session['username'] = user['username']
                return redirect(url_for('welcome'))
            else:
                flash("Invalid credentials", "danger")
                return render_template("login.html")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "danger")
            return render_template("login.html")
        finally:
            conn.close()
    
    return render_template("login.html")

@app.route('/welcome')
def welcome():
    if 'username' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    return render_template("welcome.html", username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)