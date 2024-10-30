'''
    File contains the forms for the gym log application. Thank you WTFORMS for making this easy.
'''

import wtforms
from wtforms import Form, StringField, PasswordField, validators

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
    rfid = StringField('', [validators.DataRequired()])