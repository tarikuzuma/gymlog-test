'''
    Configuration file for the Flask application
'''

SECRET_KEY = 'your_secret_key_here'
SQLALCHEMY_DATABASE_URI = 'sqlite:///spGYM_Log.db' # Database name
SQLALCHEMY_TRACK_MODIFICATIONS = False
# JOBS_FREQUENCY = 60 # in seconds (not yet implemented)
