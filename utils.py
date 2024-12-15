# All the imports are here
import os
import json
from collections import defaultdict
from datetime import datetime
from models import db, StudentData

# All the functions are here

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
def logout_all_users(app):
    with app.app_context():
        online_users = StudentData.query.filter_by(status='online').all()
        for user in online_users:
            user.status = 'offline'
            user.last_gym = datetime.now().replace(microsecond=0)
            if user.last_login:
                user.total_workout_time += (user.last_gym - user.last_login).total_seconds() / 60
            log_user_today(user)
        db.session.commit()
    print(f"{get_current_datetime()[0]} {get_current_datetime()[1]} : All users logged out due to server shutdown.")

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

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)