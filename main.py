import atexit
import os
import json
from collections import defaultdict
from flask import Flask, redirect, url_for, render_template, request, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from models import db, StudentData
from forms import RegGymLogForm, LoginForm

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

# Suppress werkzeug logging to console (COMMENT OUT IF NOT NEEDED)
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Utility function for date and time formatting
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%B %d, %Y"), now.strftime("%H:%M:%S")

# Toggle user gym status
def toggle_gym_status(user):
    now = datetime.now()
    if user.status == 'offline':
        user.status = 'online'
        user.last_login = now
        print (f"{get_current_datetime()[1]} : {user.full_name} logged in.")
    else:
        user.status = 'offline'
        user.last_gym = now.replace(microsecond=0)
        if user.last_login:
            workout_duration = round((now - user.last_login).total_seconds() / 60, 2)
            user.total_workout_time += workout_duration
        user.completed_sessions += 1
        print (f"{get_current_datetime()[1]} : {user.full_name} logged out.")
    user.last_gym_formatted = user.last_gym.strftime("%B %d, %Y %H:%M:%S") if user.last_gym else None
    db.session.commit()

# Log out all users on server shutdown
def logout_all_users():
    with app.app_context():
        online_users = StudentData.query.filter_by(status='online').all()
        for user in online_users:
            user.status = 'offline'
            user.last_gym = datetime.now()
            if user.last_login:
                user.total_workout_time += (user.last_gym - user.last_login).total_seconds() / 60
            log_user_today(user)
        db.session.commit()
    print(f"{get_current_datetime()[0]} {get_current_datetime()[1]} : All users logged out due to server shutdown.")

atexit.register(logout_all_users)

# Log user data
def log_user_today(user):
    today = datetime.now().strftime('%m-%d-%Y')
    filepath = os.path.join('Logs', f"{today}.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    workout_time = None
    workout_end = None
    if user.status == 'offline' and user.last_login and user.last_gym:
        workout_time = round((user.last_gym - user.last_login).total_seconds() / 60, 2)
        workout_end = user.last_gym.strftime("%H:%M:%S")

    user_log = {
        "full_name": user.full_name,
        "student_id": user.student_id,
        "enrolled_block": user.enrolled_block,
        "pe_course": user.pe_course,
        "workout_start": user.last_login.strftime("%H:%M:%S") if user.last_login else None,
        "last_gym": user.last_gym.strftime("%B %d, %Y %H:%M:%S") if user.last_gym else None,
        "workout_end": workout_end,
        "workout_time": workout_time if workout_time else "Workout ongoing",
        "completed_sessions": user.completed_sessions
    }

    if not os.path.isfile(filepath):
        with open(filepath, 'w') as file:
            json.dump([], file)

    with open(filepath, 'r+') as file:
        data = json.load(file)
        data.append(user_log)
        file.seek(0)
        json.dump(data, file, indent=4)
    print (f"{get_current_datetime()[1]} : {user.full_name} log saved")

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/stats_route', methods=['GET', 'POST'])
def stats_route():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = StudentData.query.filter_by(rfid=form.rfid.data).first()
        if user:
            return redirect(url_for('individual_stats', user_id=user.student_id))
        flash('RFID not recognized. Please try again.', 'error')
    return render_template('stats_forms.html', form=form)

@app.route('/individual_stats/<string:user_id>')
def individual_stats(user_id):
    user = StudentData.query.filter_by(student_id=user_id).first_or_404()
    logs_directory = 'logs'
    workout_data = defaultdict(float)
    all_dates = {filename[:-5] for filename in os.listdir(logs_directory) if filename.endswith('.json')}

    for date in all_dates:
        workout_data[date] = 0.0

    for filename in os.listdir(logs_directory):
        if filename.endswith('.json'):
            with open(os.path.join(logs_directory, filename), 'r') as file:
                for entry in json.load(file):
                    if entry['student_id'] == user_id and entry['workout_time'] != "Workout ongoing":
                        workout_data[filename[:-5]] += float(entry['workout_time'])

    return render_template(
        'individual_stats.html', 
        user=user, 
        workout_days=sorted(workout_data.keys()), 
        workout_times=[workout_data[day] for day in sorted(workout_data.keys())]
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegGymLogForm(request.form)
    if request.method == 'POST' and form.validate():
        if StudentData.query.filter(
                (StudentData.student_id == form.student_id.data) | 
                (StudentData.rfid == form.rfid.data)
            ).first():
            flash('Duplicate Student ID or RFID. Please use a different one.', 'error')
            return render_template('register.html', form=form)

        new_user = StudentData(
            full_name=form.full_name.data,
            student_id=form.student_id.data,
            pe_course=form.pe_course.data,
            enrolled_block=form.enrolled_block.data,
            rfid=form.rfid.data
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

# Route for all gym loggers
@app.route('/gym_info')
def gym_info():
    all_logs = StudentData.query.all()
    all_logs = sorted(all_logs, key=lambda log: log.status != 'online')
    return render_template('gym_info.html', all_logs=all_logs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        rfid = request.form.get('rfid')
        user = StudentData.query.filter_by(rfid=rfid).first()
        if user:
            toggle_gym_status(user)
            return redirect(url_for('toggle_gym_status_route', user_id=user.student_id))
        flash("RFID Not Recognized. Please Register.", "error")
    return render_template('login.html', form=LoginForm())

@app.route('/toggle_gym_status/<string:user_id>', methods=['GET'])
def toggle_gym_status_route(user_id):
    user = StudentData.query.filter_by(student_id=user_id).first_or_404()
    if user.status == 'offline':
        # Calculate workout time in minutes
        workout_time = round((datetime.now() - user.last_login).total_seconds() / 60, 2)
        workout_time_message = f"{workout_time} minutes"
        log_user_today(user)
    else:
        workout_time_message = "Ongoing"
    return render_template('user_auth.html', user=user, workout_time=workout_time_message)

@app.route('/daily_login_report/')
def daily_login_report_dates():
    logs_directory = 'logs'
    all_dates = {filename[:-5] for filename in os.listdir(logs_directory) if filename.endswith('.json')}
    return render_template('daily_login_report_dates.html', dates=sorted(all_dates))

@app.route('/daily_login_report/<string:date>')
def daily_login_report(date):
    filepath = os.path.join('logs', f"{date}.json")
    log_entries = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            log_entries = json.load(file)
    return render_template('daily_login_report.html', date=date, log_entries=log_entries)

if __name__ == "__main__":
    print (f"{get_current_datetime()[0]} {get_current_datetime()[1]} : Starting server...")
    print(f"{get_current_datetime()[0]} {get_current_datetime()[1]} : Hello, welcome to the Gym Logger!")
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
