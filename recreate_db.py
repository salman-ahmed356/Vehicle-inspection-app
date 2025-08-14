#!/usr/bin/env python3

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['FLASK_APP'] = 'run.py'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'

try:
    from app import create_app
    from app.database import db
    
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database recreated successfully!")
        
except Exception as e:
    print(f"Error recreating database: {e}")
    # Try without weasyprint
    try:
        # Temporarily disable weasyprint import
        import sys
        sys.modules['weasyprint'] = None
        
        from app import create_app
        from app.database import db
        
        app = create_app()
        
        with app.app_context():
            db.create_all()
            print("Database recreated successfully (without weasyprint)!")
            
    except Exception as e2:
        print(f"Error even without weasyprint: {e2}")