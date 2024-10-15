from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StudentData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(15), nullable=False, unique=True)
    pe_course = db.Column(db.String(10), nullable=False)
    enrolled_block = db.Column(db.String(10), nullable=False)
    rfid = db.Column(db.String(50), nullable=False, unique=True)
    status = db.Column(db.String(10), nullable=False, default='offline')  # online or offline
    last_gym = db.Column(db.DateTime, nullable=True)  # DateTime of last gym session end
    total_workout_time = db.Column(db.Float, nullable=False, default=0.0)  # Total workout time in minutes
    last_login = db.Column(db.DateTime, nullable=True)  # DateTime of last gym session start
    completed_sessions = db.Column(db.Integer, nullable=False, default=0)  # Number of completed gym sessions