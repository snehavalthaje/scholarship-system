🎓 Scholarship Management System

A Flask-based web application that allows students to view and apply for scholarships while enabling admins to manage scholarship records, applications, and approvals. This project simplifies the scholarship process and maintains structured digital records.

✅ Features
👩‍🎓 Student Module

View available scholarships

Submit applications

Upload required details

Track status

🛂 Admin Module

Add, edit & delete scholarships

Review student applications

Approve / reject entries

Manage records in one place

⚙️ System Capabilities

SQLite database storage

Modular folder structure

HTML templates with CSS styling

Form validation

Error handling & logs

🛠️ Tech Stack
Layer	Technology
Backend	Python, Flask
Frontend	HTML, CSS, Bootstrap
Database	SQLite
Tools	Git, VS Code
📂 Project Structure
scholarship_system/
│
├── app.py
├── init_db.py
├── scholarship.db
├── app.log
│
├── static/          # CSS, images, JS
├── templates/       # HTML files
├── instance/        # Config & DB (ignored)
├── venv/            # Virtual environment
│
└── requirements.txt

🚀 Run the Project Locally
1️⃣ Clone the repository
git clone https://github.com/snehavalthaje/scholarship-system.git
cd scholarship-system

2️⃣ Create & activate virtual environment
python -m venv venv
venv\Scripts\activate       # Windows

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the server
python app.py

5️⃣ Open in browser
http://127.0.0.1:5000/

✅ .gitignore (Important)
venv/
__pycache__/
instance/
*.db
*.log
.env

📌 Future Enhancements

User authentication (login/signup)

Email notifications

Admin dashboard UI improvements

Cloud deployment (Render/Railway)
