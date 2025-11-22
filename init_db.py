import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="4JK23CS106",
    database="scholarship_db"
)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS students")
cursor.execute('''
    CREATE TABLE students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        course VARCHAR(100) NOT NULL,
        cgpa FLOAT NOT NULL
    )
''')

conn.commit()
conn.close()
