#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

def test_imports():
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print("✓ Flask-SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ Flask-SQLAlchemy import failed: {e}")
        return False
    
    try:
        import flask_wtf
        print("✓ Flask-WTF imported successfully")
    except ImportError as e:
        print(f"✗ Flask-WTF import failed: {e}")
        return False
    
    try:
        import wtforms
        print("✓ WTForms imported successfully")
    except ImportError as e:
        print(f"✗ WTForms import failed: {e}")
        return False
    
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        print("✓ APScheduler imported successfully")
    except ImportError as e:
        print(f"✗ APScheduler import failed: {e}")
        return False
    
    try:
        from datetime import datetime
        print("✓ datetime imported successfully")
    except ImportError as e:
        print(f"✗ datetime import failed: {e}")
        return False
    
    try:
        import json
        print("✓ json imported successfully")
    except ImportError as e:
        print(f"✗ json import failed: {e}")
        return False
    
    try:
        import os
        print("✓ os imported successfully")
    except ImportError as e:
        print(f"✗ os import failed: {e}")
        return False
    
    try:
        from collections import defaultdict
        print("✓ collections imported successfully")
    except ImportError as e:
        print(f"✗ collections import failed: {e}")
        return False
    
    print("\nAll imports successful! ✓")
    return True

def test_local_imports():
    print("\nTesting local imports...")
    
    try:
        from models import db, StudentData
        print("✓ models imported successfully")
    except ImportError as e:
        print(f"✗ models import failed: {e}")
        return False
    
    try:
        from forms import RegGymLogForm, LoginForm
        print("✓ forms imported successfully")
    except ImportError as e:
        print(f"✗ forms import failed: {e}")
        return False
    
    try:
        from utils import get_current_datetime, toggle_gym_status, logout_all_users, log_user_today, sort_files_by_date
        print("✓ utils imported successfully")
    except ImportError as e:
        print(f"✗ utils import failed: {e}")
        return False
    
    try:
        import config
        print("✓ config imported successfully")
    except ImportError as e:
        print(f"✗ config import failed: {e}")
        return False
    
    print("All local imports successful! ✓")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("Gym Logger Import Test")
    print("=" * 50)
    
    success1 = test_imports()
    success2 = test_local_imports()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("ALL TESTS PASSED! ✓")
        print("You can now run: python main.py")
    else:
        print("SOME TESTS FAILED! ✗")
        print("Please run the installation script first:")
        print("- Windows: install.bat")
        print("- PowerShell: install.ps1")
    print("=" * 50) 