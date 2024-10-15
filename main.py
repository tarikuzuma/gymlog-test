import atexit

import os
import json
from collections import defaultdict # Import defaultdict from collections module


from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import wtforms
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SubmitField


app = Flask(__name__)

app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spGYM_Log.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
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

class RegGymLogForm(Form):
    full_name = StringField('Full Name', [validators.Length(min=2, max=100), validators.DataRequired()])
    student_id = StringField('Student ID Number', [validators.Length(min=9, max=13), validators.DataRequired()])
    pe_course = wtforms.SelectField('PE Course', choices=[
        ('pedu1', 'PEEDU1'),
        ('pedu2', 'PEEDU2'),
        ('pedu3', 'PEEDU3'),
        ('pedu4', 'PEEDU4'),
        ('none', 'None')
    ], validators=[validators.DataRequired()])
    enrolled_block = StringField('Enrolled Block', [validators.Length(min=3, max=9), validators.DataRequired()])
    rfid = StringField('APC Identification Card', [validators.DataRequired()])

class LoginForm(Form):
    rfid = StringField('RFID', [validators.DataRequired()])

############################################################################################################

def get_current_datetime():
    now = datetime.now()
    return {
        'date': now.strftime("%B %d, %Y"),
        'time': now.strftime("%H:%M:%S"),
        'day': now.strftime("%A")
    }

# Function to toggle gym status of user
def toggle_gym_status(user):
    if user.status == 'offline':
        # If the user is offline, log them in
        user.status = 'online'
        user.last_login = datetime.now()  # Record login time
        print (f"User {user.full_name} logged in at {user.last_login}.")
    
    elif user.status == 'online':
        # If the user is online, log them out
        user.status = 'offline'
        
        user.last_gym = datetime.now()  # Record logout time
        print (f"User {user.full_name} logged out at {user.last_gym}.")
        
        # Calculate workout duration in minutes and add to total_workout_time
        if user.last_login:
            duration = round((datetime.now() - user.last_login).total_seconds() / 60, 2)
            user.total_workout_time += duration
        

        user.completed_sessions += 1
    
    db.session.commit()

# Function to log out all users when the server is shut down
def logout_all_users():
    with app.app_context():
        online_users = StudentData.query.filter_by(status='online').all()
        for user in online_users:
            user.status = 'offline'
            user.completed_sessions += 1
            user.last_gym = datetime.now()
            if user.last_login:
                duration = (user.last_gym - user.last_login).total_seconds() / 60
                user.total_workout_time += duration
            print(f"User {user.full_name} logged out at {user.last_gym}. due to server shutdown.")
            log_user_today(user)
        db.session.commit()

    current_datetime = get_current_datetime()

    print(f"{current_datetime['date']} {current_datetime['time']} : All users logged out due to server shutdown.")

atexit.register(logout_all_users)

# Log users who logged in today in a JSON file
# Function to log users who logged in today in a JSON file
def log_user_today(user):
    today = datetime.now().strftime('%m-%d-%Y')
    directory = 'Logs'
    filename = f"{today}.json"
    
    # Create Logs directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    filepath = os.path.join(directory, filename)
    
    # Check if the file already exists
    if not os.path.exists(filepath):
        with open(filepath, 'w') as file:
            json.dump([], file)  # Create an empty JSON array

    # Calculate workout time if the workout has ended
    workout_time = None
    workout_end = None
    if user.status == 'offline' and user.last_login and user.last_gym:
        workout_time = round((user.last_gym - user.last_login).total_seconds() / 60, 2)
        workout_end = user.last_gym.strftime("%H:%M:%S")
    
    # Prepare the user's log data
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

    # Append the log to the JSON file
    with open(filepath, 'r+') as file:
        data = json.load(file)
        data.append(user_log)
        file.seek(0)
        json.dump(data, file, indent=4)

    print(f"{user.full_name} log saved")

############################################################################################################

@app.route('/')
def home():
    #return render_template('index.html')
    return redirect(url_for('login'))

# Route to display stats form
@app.route('/stats_route', methods=['GET', 'POST'])
def stats_route():
    form = LoginForm(request.form)
    if request.method == 'POST':
        print("Stats submitted.")
        if form.validate():
            rfid = form.rfid.data
            print(f"RFID: {rfid}")
            user = StudentData.query.filter_by(rfid=rfid).first()
            if user:
                print("STATS LOADING...")
                return redirect(url_for('individual_stats', user_id=user.student_id))
            else:
                print('RFID not recognized. Please try again.')
        else:
            print("Form validation failed.")
    return render_template('stats_forms.html', form=form)

# Route to display stats form
@app.route('/individual_stats/<string:user_id>')
def individual_stats(user_id):
    user = StudentData.query.filter_by(student_id=user_id).first_or_404()
    logs_directory = 'logs'
    workout_data = defaultdict(float)
    
    # Step 1: Gather all dates from the logs
    all_dates = set()

    for filename in os.listdir(logs_directory):
        if filename.endswith('.json'):
            all_dates.add(filename[:-5])  # Extract the date part (MM-DD-YY)

    # Initialize workout_data with all dates
    for date in all_dates:
        workout_data[date] = 0.0

    # Step 2: Iterate through logs and populate workout data
    for filename in os.listdir(logs_directory):
        if filename.endswith('.json'):
            filepath = os.path.join(logs_directory, filename)
            with open(filepath, 'r') as file:
                log_entries = json.load(file)

                # Check each log entry
                for entry in log_entries:
                    if entry['student_id'] == user_id:
                        # Add workout time for that day
                        if entry['workout_time'] != "Workout ongoing":
                            workout_data[filename[:-5]] += float(entry['workout_time'])

    # Prepare data for the graph
    workout_days = sorted(workout_data.keys())  # X-axis: Days
    workout_times = [workout_data[day] for day in workout_days]  # Y-axis: Total Workout Time

    # Render the graph
    return render_template(
        'individual_stats.html', 
        user=user, 
        workout_days=workout_days, 
        workout_times=workout_times
    )


# Route to register gym log
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegGymLogForm(request.form)
    if request.method == 'POST' and form.validate():

        # Check for duplicate student_id or RFID
        existing_user = StudentData.query.filter(
            (StudentData.student_id == form.student_id.data) | 
            (StudentData.rfid == form.rfid.data)
        ).first()

        if existing_user:
            flash('A user with this Student ID or RFID already exists. Please use a different one.', 'error')
            return render_template('register.html', form=form)

        # If no duplicate is found, proceed with registration
        gym_log_entry = StudentData(
            full_name=form.full_name.data,
            student_id=form.student_id.data,
            pe_course=form.pe_course.data,
            enrolled_block=form.enrolled_block.data,
            rfid=form.rfid.data
        )
        db.session.add(gym_log_entry)
        db.session.commit()
        print(f'Gym log submitted successfully! New user, {form.full_name.data}, has been registered. at {datetime.now()}')
        return redirect(url_for('home'))

    return render_template('register.html', form=form)
    

# Route to display all gym logs
@app.route('/gym_info')
def gym_info():
    all_logs = StudentData.query.all()

    # round up last_gym time to the nearest seconds
    for log in all_logs:
        if log.last_gym:
            log.last_gym = log.last_gym.strftime("%B %d, %Y %H:%M:%S")


    return render_template('gym_info.html', all_logs=all_logs)

# Route to display login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        print("Form submitted.")
        if form.validate():
            print("Form validated.")
            rfid = form.rfid.data
            print(f"RFID: {rfid}")
            user = StudentData.query.filter_by(rfid=rfid).first()
            if user:
                print("RFID recognized.")
                toggle_gym_status(user)
                return redirect(url_for('toggle_gym_status_route', user_id=user.student_id))  # Corrected with user_id in URL
            else:
                flash("RFID Not Recognized. Please Register.", "error")  # Flash message for unrecognized RFID
        else:
            print("Form validation failed.")
            flash("Form validation failed. Please check your input.", "error")  # Flash message for validation failure

    return render_template('login.html', form=form)


# Route to toggle status of student
# Redirect user to
@app.route('/toggle_gym_status/<string:user_id>', methods=['GET'])
def toggle_gym_status_route(user_id):
    user = StudentData.query.filter_by(student_id=user_id).first_or_404()
    if user.status == 'online':
        message = 'User is currently logged in.'
        message2 = 'Welcome'
    elif user.status == 'offline':
        message = 'User is currently logged out.'
        message2 = 'Goodbye'
        log_user_today(user)
    
    return render_template('user_auth.html', user=user, message=message, message2=message2)

# Route to display available dates for daily login report
@app.route('/daily_login_report/')
def daily_login_report_dates():
    logs_directory = 'logs'
    all_dates = set()

    # Retrieve all JSON log files in the logs directory
    for filename in os.listdir(logs_directory):
        if filename.endswith('.json'):
            # Extract the date part from the filename (assumed to be MM-DD-YEAR.json)
            date_str = filename[:-5]  # Remove the '.json' extension
            all_dates.add(date_str)

    # Sort the dates (if necessary)
    sorted_dates = sorted(all_dates)

    return render_template('daily_login_report_dates.html', dates=sorted_dates)


# Route to display who logged in for a certian day
# If the name of the day is August 11, 2024, the date is August 11, 2024
@app.route('/daily_login_report/<string:date>')
def daily_login_report(date):
    directory = 'logs'
    filename = f"{date}.json"
    filepath = os.path.join(directory, filename)

    if not os.path.exists(filepath):
        return render_template('daily_login_report.html', date=date, log_entries=[])
    
    with open(filepath, 'r') as file:
        log_entries = json.load(file)
    
    return render_template('daily_login_report.html', date=date, log_entries=log_entries)

    
############################################################################################################
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)