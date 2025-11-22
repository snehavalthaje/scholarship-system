import requests
from flask import Flask, render_template, request, session,flash,redirect
from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from bs4 import BeautifulSoup
from werkzeug.security import check_password_hash

app = Flask(__name__)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Ensure it's just "root", not "root@localhost"
        password="4JK23CS106",  # This should match your MySQL password
        database="scholarship_db"
    )
# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# Route to display students
@app.route('/students')
def students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")
    students_data = cursor.fetchall()

    conn.close()
    
    print(students_data)  # 🔍 Debugging: Print student records in terminal

    return render_template("students.html", students=students_data)


# Route to add a student
import bcrypt
from flask import Flask, render_template, request, redirect, session

app.secret_key = "supersecretkey"

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        course = request.form['course']
        cgpa = request.form['cgpa']

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password, course, cgpa) VALUES (%s, %s, %s, %s, %s)",
                       (name, email, hashed_pw, course, cgpa))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")  # 🔥 Renaming signup to register


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            session['user_id'] = user["id"]
            return redirect('/dashboard')
        else:
            return "Invalid credentials. Try again."

    return render_template("login.html")  # 🔥 Fix: Handle GET requests properly


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch user details
        cursor.execute("SELECT name, course, cgpa FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()

        # Fetch applied scholarships with status
        cursor.execute("""
            SELECT scholarships.name, scholarships.amount, applications.status, applications.updated_at
            FROM applications
            JOIN scholarships ON applications.scholarship_id = scholarships.id
            WHERE applications.user_id = %s
            ORDER BY applications.updated_at DESC
        """, (session['user_id'],))
        applied_scholarships = cursor.fetchall()

        conn.close()
        return render_template("dashboard.html", user=user, applied_scholarships=applied_scholarships)

    return redirect('/login')

@app.route('/schemes', methods=['GET', 'POST'])
def schemes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Base Query
    query = "SELECT * FROM scholarships WHERE 1=1"
    filters = []

    # ✅ Extract Filters
    name_filter = request.form.get("name")
    min_cgpa = request.form.get("min_cgpa")

    # ✅ Apply Filters
    if name_filter:
        query += " AND name LIKE %s"
        filters.append(f"%{name_filter}%")

    if min_cgpa:
        query += " AND eligibility LIKE %s"
        filters.append(f"CGPA: {min_cgpa}%")  # ✅ Matches CGPA values

    # ✅ Order Scholarships by CGPA Requirement
    query += " ORDER BY CAST(SUBSTRING_INDEX(eligibility, ':', -1) AS DECIMAL) DESC"

    # ✅ Execute Query Based on Filters
    if filters:
        cursor.execute(query, tuple(filters))
    else:
        cursor.execute(query)

    schemes = cursor.fetchall()
    conn.close()

    return render_template('schemes.html', schemes=schemes)


@app.route('/apply/<int:scholarship_id>', methods=['POST'])
def apply(scholarship_id):
    if 'user_id' not in session:  # 🔐 Ensure user is logged in
        flash("Please log in to apply!", "danger")
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ✅ Fetch the scholarship scheme details
    cursor.execute("SELECT * FROM scholarships WHERE id = %s", (scholarship_id,))
    scheme = cursor.fetchone()

    if not scheme:
        flash("Scholarship not found!", "danger")
        return redirect('/schemes')

    # ✅ Insert application with scholarship scheme details
    cursor.execute(
        "INSERT INTO applications (user_id, scholarship_id, status) VALUES (%s, %s, %s)",
        (session['user_id'], scholarship_id, 'Pending')
    )
    conn.commit()
    conn.close()

    flash(f"Successfully applied for {scheme['name']}!", "success")  # 🎉 Notify user
    return redirect('/dashboard')



@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()
        conn.close()

        if admin and check_password_hash(admin['password'], password):  
            session['admin_id'] = admin['id']
            return redirect(url_for('admin_dashboard'))  # Redirect to dashboard after login
        else:
            flash("Invalid credentials", "danger")

    return render_template('admin_login.html')  # Now this exists!


@app.route('/admin_dashboard')
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT applications.id, users.name AS student_name, scholarships.name AS scholarship_name, applications.status
        FROM applications
        JOIN users ON applications.user_id = users.id
        JOIN scholarships ON applications.scholarship_id = scholarships.id
        WHERE applications.status = 'Pending'
    """)
    pending_applications = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', pending_applications=pending_applications)



@app.route('/approve/<int:app_id>', methods=['POST'])
def approve_application(app_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status = 'Approved' WHERE id = %s", (app_id,))
    conn.commit()
    conn.close()
    flash("Application Approved!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/reject/<int:app_id>', methods=['POST'])
def reject_application(app_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status = 'Rejected' WHERE id = %s", (app_id,))
    conn.commit()
    conn.close()
    flash("Application Rejected!", "danger")
    return redirect(url_for('admin_dashboard'))


@app.route('/about')
def about():
    return render_template("about.html")
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change for other providers
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_email_password'   # Use an App Password, not a real password!

mail = Mail(app)
def send_email(to_email, subject, body):
    msg = Message(subject, sender='your_email@gmail.com', recipients=[to_email])
    msg.body = body
    mail.send(msg)

if __name__ == "__main__":
    app.run(debug=True, port=5000)