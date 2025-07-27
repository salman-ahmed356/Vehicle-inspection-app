from flask import session, redirect, url_for, request, flash, abort
from datetime import datetime, timedelta
from functools import wraps
from .models import Staff

# Define role hierarchy
ROLES = {
    'admin': 3,
    'manager': 2,
    'worker': 1
}

def get_current_user():
    """Get current user from session"""
    if 'user_id' in session:
        return Staff.query.get(session['user_id'])
    return None

def has_role(required_role):
    """Check if current user has required role or higher"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    user_role_level = ROLES.get(current_user.role.lower(), 0)
    required_role_level = ROLES.get(required_role.lower(), 0)
    
    return user_role_level >= required_role_level

def role_required(required_role):
    """Decorator to require specific role or higher"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or 'expiry' not in session:
                return redirect(url_for('auth.login', next=request.url))
            
            # Check if session has expired
            if datetime.now() > datetime.fromisoformat(session['expiry']):
                session.clear()
                flash('Your session has expired. Please login again.', 'error')
                return redirect(url_for('auth.login', next=request.url))
            
            # Check role permission
            if not has_role(required_role):
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('main.index'))
            
            # Extend session expiry on activity
            session['expiry'] = (datetime.now() + timedelta(hours=3)).isoformat()
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def can_edit_staff(target_staff_id):
    """Check if current user can edit target staff member"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    # Admin can edit anyone
    if current_user.role.lower() == 'admin':
        return True
    
    # Users can edit themselves
    if current_user.id == target_staff_id:
        return True
    
    # Manager can edit workers they added
    if current_user.role.lower() == 'manager':
        target_staff = Staff.query.get(target_staff_id)
        if target_staff and target_staff.role.lower() == 'worker':
            return True
    
    return False

def can_delete_staff(target_staff_id):
    """Check if current user can delete target staff member"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    target_staff = Staff.query.get(target_staff_id)
    if not target_staff:
        return False
    
    # Admin can delete anyone except themselves
    if current_user.role.lower() == 'admin':
        return current_user.id != target_staff_id
    
    # Manager can delete workers they added
    if current_user.role.lower() == 'manager':
        return target_staff.role.lower() == 'worker'
    
    return False

def can_add_staff():
    """Check if current user can add staff members"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    # Admin and Manager can add staff
    return current_user.role.lower() in ['admin', 'manager']

def get_visible_staff():
    """Get staff members visible to current user"""
    current_user = get_current_user()
    if not current_user:
        return []
    
    # Admin sees everyone
    if current_user.role.lower() == 'admin':
        return Staff.query.all()
    
    # Manager sees themselves and workers
    elif current_user.role.lower() == 'manager':
        return Staff.query.filter(Staff.role.in_(['manager', 'worker'])).all()
    
    # Worker sees only themselves
    else:
        return [current_user]

def can_delete_reports():
    """Check if current user can delete reports"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    # Only admin can delete reports
    return current_user.role.lower() == 'admin'

def can_delete_customers():
    """Check if current user can delete customers"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    # Only admin can delete customers
    return current_user.role.lower() == 'admin'

def can_access_company_settings():
    """Check if current user can access company settings"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    # Only admin can access company settings
    return current_user.role.lower() == 'admin'

def can_access_logs():
    """Check if current user can access system logs"""
    current_user = get_current_user()
    if not current_user:
        return False
    
    # Only admin can access logs
    return current_user.role.lower() == 'admin'