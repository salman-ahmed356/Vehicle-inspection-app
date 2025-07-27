#!/usr/bin/env python3
"""
Setup script for Role-Based Access Control (RBAC) system
This script creates the necessary database tables and sets up initial data
"""

import os
import sys
from flask import Flask
from app import create_app
from app.database import db
from app.models import SystemLog, Staff
from werkzeug.security import generate_password_hash

def setup_database():
    """Create database tables and setup initial data"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Check if we need to create an admin user
            admin_user = Staff.query.filter_by(role='admin').first()
            if not admin_user:
                # Get the first branch or create one
                from app.models import Branch, Company, Address
                branch = Branch.query.first()
                if not branch:
                    # Create minimal company structure if none exists
                    address = Address(street_address="Default", city="Default")
                    db.session.add(address)
                    db.session.flush()
                    
                    company = Company(name="Default Company", address_id=address.id)
                    db.session.add(company)
                    db.session.flush()
                    
                    branch = Branch(name="Main", company_id=company.id, address_id=address.id)
                    db.session.add(branch)
                    db.session.flush()
                
                # Create default admin user
                admin = Staff(
                    first_name="Admin",
                    last_name="User",
                    password=generate_password_hash("admin123", method='pbkdf2:sha256', salt_length=16),
                    phone_number="000-000-0000",
                    department="Management",
                    role="admin",
                    branch_id=branch.id
                )
                
                try:
                    db.session.add(admin)
                    db.session.commit()
                    print("✓ Default admin user created (phone: 000-000-0000, password: admin123)")
                except Exception as e:
                    print(f"⚠ Could not create admin user: {e}")
                    db.session.rollback()
            else:
                print("✓ Admin user already exists")
            
            # Create initial log entry
            from app.services.log_service import log_action
            try:
                log_action('SYSTEM_SETUP', 'RBAC system initialized', admin_user.id if admin_user else None)
                print("✓ Initial system log created")
            except Exception as e:
                print(f"⚠ Could not create initial log: {e}")
            
            print("\n🎉 RBAC setup completed successfully!")
            print("\nRole-based access control features:")
            print("- Admin: Full system access")
            print("- Manager: Can manage workers, create reports, view all data")
            print("- Worker: Can create reports, edit own profile only")
            print("\nAdmin features:")
            print("- System logs accessible via Settings > System Logs")
            print("- Company settings restricted to admin only")
            print("- Full staff management capabilities")
            
        except Exception as e:
            print(f"❌ Error setting up database: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("Setting up Role-Based Access Control (RBAC) system...")
    print("=" * 50)
    
    if setup_database():
        print("\n✅ Setup completed successfully!")
        print("\nYou can now run the application with: python run.py")
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)