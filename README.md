
# Gym Logger System

A Flask-based gym tracking system for managing student workout sessions.

## Features

- ✅ **Student Registration** - Register new students with RFID cards
- ✅ **Gym Login/Logout** - Track student gym sessions
- ✅ **Real-time Status** - See who's currently in the gym
- ✅ **Individual Statistics** - View detailed workout history per student
- ✅ **Search Students** - Find students by name or ID
- ✅ **Date Filtering** - Filter statistics by date range
- ✅ **Printable Reports** - Print all reports and statistics
- ✅ **Student Summary** - Comprehensive student performance reports
- ✅ **Accurate Time Tracking** - Precise workout time calculations
- ✅ **Session Counting** - Accurate completed session tracking

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10/11

### Quick Setup

1. **Download Python** (if not installed):
   - Go to https://python.org
   - Download Python 3.8+ for Windows
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**:
   - Double-click `install.bat` (Command Prompt) OR
   - Right-click `install.ps1` → "Run with PowerShell"

3. **Test Installation**:
   ```
   python test_imports.py
   ```

4. **Run the Application**:
   ```
   python main.py
   ```

5. **Access the System**:
   - Open your web browser
   - Go to: http://localhost:5001

## Manual Installation

If the automatic installation doesn't work:

1. **Open Command Prompt** in the gymlog-test folder
2. **Install dependencies**:
   ```cmd
   pip install Flask==2.3.3 Flask-SQLAlchemy==3.0.5 Flask-WTF==1.1.1 WTForms==3.0.1 APScheduler==3.10.4 Werkzeug==2.3.7
   ```
3. **Run the application**:
   ```cmd
   python main.py
   ```

## Troubleshooting

### Import Errors
If you get import errors:

1. **Check Python installation**:
   ```cmd
   python --version
   ```

2. **Check pip installation**:
   ```cmd
   pip --version
   ```

3. **Upgrade pip**:
   ```cmd
   python -m pip install --upgrade pip
   ```

4. **Reinstall dependencies**:
   ```cmd
   pip uninstall flask flask-sqlalchemy flask-wtf wtforms apscheduler werkzeug
   pip install -r requirements.txt
   ```

### Common Issues

- **"python not found"**: Install Python and add to PATH
- **"pip not found"**: Run `python -m ensurepip --upgrade`
- **Permission errors**: Run Command Prompt as Administrator
- **Port already in use**: Change port in main.py line 186

## System Features

### Main Pages
- **Login Page** (`/`) - RFID card login
- **Gym Info** (`/gym_info`) - View all students and current status
- **Search Students** (`/search_students`) - Find students by name/ID
- **Student Summary** (`/student_summary`) - Comprehensive reports
- **Individual Stats** (`/individual_stats/<student_id>`) - Personal statistics

### Key Improvements Made
- ✅ Fixed accurate hour calculations
- ✅ Added student search functionality
- ✅ Implemented date filtering for stats
- ✅ Made all reports printable
- ✅ Fixed accurate session counting
- ✅ Separated student data properly
- ✅ Added date and time summaries

## File Structure

```
gymlog-test/
├── main.py              # Main application
├── models.py            # Database models
├── forms.py             # Web forms
├── utils.py             # Utility functions
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── install.bat         # Windows installer
├── install.ps1         # PowerShell installer
├── test_imports.py     # Import test script
├── templates/          # HTML templates
├── static/            # CSS, JS, images
├── logs/              # Workout logs (JSON)
└── instance/          # Database files
```

## Usage

1. **Start the system**: `python main.py`
2. **Register students**: Go to `/register`
3. **Login students**: Use RFID cards at `/`
4. **View statistics**: Use search or individual stats pages
5. **Print reports**: Click "Print Report" buttons

## Support

If you encounter any issues:
1. Run `python test_imports.py` to check dependencies
2. Check the console output for error messages
3. Ensure all files are in the correct directory structure
4. Make sure Python 3.8+ is installed and in PATH
