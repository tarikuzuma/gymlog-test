
# Gym Log App for APC Gym

Welcome to the Gym Log App for APC Gym! This application is designed to help users log their workouts, track progress, and manage gym-related data effectively.

## Getting Started

To get started with the Gym Log App, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone <your-repository-url>
   cd <your-repository-folder>
   ```

2. **Install Requirements**
   Make sure you have Python and pip installed on your machine. Run the following command to install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   You can also use a virtual environment for better dependency management. If you prefer using a virtual environment, create one using:
   ```bash
   python -m venv venv
   ```
   Activate it with the command:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

## Running Commands

To run commands for the application, set the `FLASK_APP` environment variable and execute the desired command.

### Example Command
Set the `FLASK_APP` variable:
```bash
set FLASK_APP=commands.py  # On Windows
$env:FLASK_APP="commands.py" # On CMD or PowerShell
export FLASK_APP=commands.py  # On macOS/Linux
```

Then, seed the database or run tests with the following command:
```bash
flask seeder:tests
```

## Features

- User registration and login
- Workout logging and tracking
- Progress visualization
- Database management

## Contributing

We welcome contributions! If you'd like to contribute, please fork the repository and submit a pull request.
