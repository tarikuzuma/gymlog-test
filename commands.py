'''
    ONLY USE THIS FILE AND COMMANDS FOR TESTING.
    DO NOT PUSH TO PRODUCTION.

    All Seeder Commands are located  in seeders folder.
'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config') 

from models import db, StudentData

db.init_app(app)

# Seed database with test data
@app.cli.command("seeder:tests")
def seeder_db():
    with app.app_context():
        answer = input("This will delete all data in the database. Are you sure you want to proceed? (y/n): ")
        if answer.lower() == 'y':
            db.drop_all()
            print ("Database dropped.")
            db.create_all()
            print ("Database created.")

            json_file_path = 'seeders/database/test_students.json'

            try:
                with open(json_file_path, 'r') as file:
                    test_data = json.load(file)  # Load the JSON data
            except FileNotFoundError:
                print(f"Error: The file {json_file_path} does not exist.")
                return

            for data in test_data:
                student = StudentData(
                    full_name=data["full_name"],
                    student_id=data["student_id"],
                    enrolled_block=data["enrolled_block"],
                    pe_course=data["pe_course"],
                    rfid=data["rfid"],
                    status='offline',
                    total_workout_time=0.0,
                    completed_sessions=0
                )
                db.session.add(student)
                print (f"Added {data['full_name']} to the database")

            db.session.commit()
            print("Database seeded with test data.")
        else:
            print("Seeder aborted.")

# Seed logs with test logs HELP IM BRAIN FUCKED
@app.cli.command("seeder:logs")
def seeder_logs():
    answer = input("This will add dummy logs in your logs folder BUT won't delete the previous ones. Are you sure you want to proceed? (y/n): ")

    if answer.lower() == 'y':
        logs_directory = 'logs'
        logs_seed_directory = 'seeders/logs/log_test.json'

        # copy the content of the seed file to the logs folder
        with open(logs_seed_directory, 'r') as file:
            logs_seed = json.load(file)
        
    else:
        print("Seeder aborted.")
