'''
    This file contains the main application logic for the Gym Logger. The application is a Flask web application that logs gym sessions of students. The application has the following features:
        - Register new students
        - Log in and log out students
        - View gym status of all students
        - View individual student stats
        - View daily login reports
'''


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
# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

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
    filepath = os.path.join('logs', f"{today}.json")
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

# Function to sort logs by date
def sort_files_by_date(path):
    file_list = os.listdir(path)
    file_list = [file for file in file_list if file.endswith('.json')]

    # Sort files by date (make sure the date format is correct)
    file_list.sort(key=lambda x: datetime.strptime(x.split('.')[0], '%m-%d-%Y'))
    logs_by_month = defaultdict(list)
    logs_by_month_and_year = []

    for file in file_list:
        date_str = file.split('.')[0]  # Extract date part from filename
        date_obj = datetime.strptime(date_str, '%m-%d-%Y')
        month_year_name = date_obj.strftime('%B %Y')

        # Append the file to the corresponding month
        logs_by_month[month_year_name].append(file)

        # Add to unique months list
        if month_year_name not in logs_by_month_and_year:
            logs_by_month_and_year.append(month_year_name)

    # Return both the structured logs and the ordered months list
    return logs_by_month_and_year, dict(logs_by_month)

# Route for home page only redirects to login page
@app.route('/')
def home():
    return redirect(url_for('login'))

# Route for accessing forms for individual student stats
@app.route('/stats_route', methods=['GET', 'POST'])
def stats_route():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = StudentData.query.filter_by(rfid=form.rfid.data).first()
        if user:
            return redirect(url_for('individual_stats', user_id=user.student_id))
        flash('RFID not recognized. Please try again.', 'error')
    return render_template('stats_forms.html', form=form)

# Route for individual student stats
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

# Route for registering new students
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

# Route for logging in and out students
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

# Route for toggling gym status
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

# Route for daily login reports in the past sessions
@app.route('/daily_login_report/')
def daily_login_report_dates():
    logs_directory = 'logs'
    all_dates = sorted(
        {datetime.strptime(filename[:-5], '%m-%d-%Y') for filename in os.listdir(logs_directory) if filename.endswith('.json')},
        reverse=True
    )
    sorted_dates = [date.strftime('%m-%d-%Y') for date in all_dates]
    logs_by_month_and_year, organized_logs = sort_files_by_date(logs_directory)
    
    # Sort the months in reverse order to start from the latest
    organized_logs = dict(sorted(organized_logs.items(), key=lambda item: datetime.strptime(item[0], '%B %Y'), reverse=True))

    # Sort dates within each month in reverse order
    for month in organized_logs:
        organized_logs[month].sort(key=lambda date: datetime.strptime(date.split('.')[0], '%m-%d-%Y'), reverse=True)

    return render_template('daily_login_report_dates.html', dates=sorted_dates, available_months=logs_by_month_and_year, organized_logs=organized_logs)

# Route for daily login reports for a specific date
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
