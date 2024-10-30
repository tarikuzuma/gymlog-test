'''
    ONLY USE THIS FILE AND COMMANDS FOR TESTING.
    DO NOT PUSH TO PRODUCTION.
'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config') 

from models import db, StudentData

db.init_app(app)

@app.cli.command("seeder:tests")
def seeder_db():
    with app.app_context():
        answer = input("This will delete all data in the database. Are you sure you want to proceed? (y/n): ")
        if answer.lower() == 'y':
            db.drop_all()
            db.create_all()

            test_data = [
                    {"full_name": "Mason K. Turner", "student_id": "2021-190076", "enrolled_block": "IT251", "pe_course": "PE1", "rfid": "0384729103"},
                    {"full_name": "Sophia A. Miller", "student_id": "2023-140021", "enrolled_block": "MMA190", "pe_course": "PE2", "rfid": "0451938201"},
                    {"full_name": "Ethan D. Rivera", "student_id": "2020-190099", "enrolled_block": "SS221", "pe_course": "PE3", "rfid": "0395820147"},
                    {"full_name": "Emma L. Garcia", "student_id": "2022-140054", "enrolled_block": "IT250", "pe_course": "PE4", "rfid": "0417283049"},
                    {"full_name": "Liam R. Johnson", "student_id": "2023-190067", "enrolled_block": "MMA195", "pe_course": "PE1", "rfid": "0471938250"},
                    {"full_name": "Olivia N. Perez", "student_id": "2020-140011", "enrolled_block": "SS222", "pe_course": "PE2", "rfid": "0326194708"},
                    {"full_name": "Noah H. Brooks", "student_id": "2021-190023", "enrolled_block": "IT251", "pe_course": "PE3", "rfid": "0345871290"},
                    {"full_name": "Isabella F. Smith", "student_id": "2022-140065", "enrolled_block": "MMA190", "pe_course": "PE4", "rfid": "0489127365"},
                    {"full_name": "Lucas J. Thompson", "student_id": "2020-140092", "enrolled_block": "SS223", "pe_course": "PE1", "rfid": "0314726958"},
                    {"full_name": "Ava E. Mitchell", "student_id": "2023-190041", "enrolled_block": "IT252", "pe_course": "PE2", "rfid": "0463021587"},
                    {"full_name": "Jose H. Nunez", "student_id": "2023-140022", "enrolled_block": "MI231", "pe_course": "PE3", "rfid": "1920983678"},
                ]
            
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

        
