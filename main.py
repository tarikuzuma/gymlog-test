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

from utils import get_current_datetime, toggle_gym_status, logout_all_users, log_user_today, sort_files_by_date

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

# Suppress werkzeug logging to console (COMMENT OUT IF NOT NEEDED)
# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

atexit.register(logout_all_users, app)

# Route for home page only redirects to login page
@app.route('/')
def home():
    return redirect(url_for('login'))

 # Route for about_us page
@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

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
    # Sort so that online users appear at the top, offline users below
    all_logs = sorted(all_logs, key=lambda log: log.status == 'offline')
    total_online = StudentData.query.filter_by(status="online").count()
    return render_template('gym_info.html', all_logs=all_logs, total_online=total_online)

# Route for logging in and out students
@app.route('/login', methods=['GET', 'POST'])
def login():
    is_registered = True
    is_full = False
    if request.method == 'POST':
        rfid = request.form.get('rfid')
        user = StudentData.query.filter_by(rfid=rfid).first()
        if user:
            if user.status == "online":
                toggle_gym_status(user)
                return redirect(url_for('toggle_gym_status_route', user_id=user.student_id))
            else:
                if StudentData.query.filter_by(status="online").count() >= app.config['MAX_USERS']:
                    is_full = True  # Gym is full, so prevent login
                else:
                    toggle_gym_status(user)
                    return redirect(url_for('toggle_gym_status_route', user_id=user.student_id))
        else:
            is_registered = False

    return render_template('login.html', form=LoginForm(), is_registered=is_registered, is_full=is_full)

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


# Route to access settings
@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == "__main__":
    print (f"{get_current_datetime()[0]} {get_current_datetime()[1]} : Starting server...")
    print(f"{get_current_datetime()[0]} {get_current_datetime()[1]} : Hello, welcome to the Gym Logger!")
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)

