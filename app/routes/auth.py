from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta

from ..database import db
from ..models import Staff
from ..auth import login_required
from ..services.log_service import log_action

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        
        staff = Staff.query.filter_by(phone_number=phone_number).first()
        
        if staff and check_password_hash(staff.password, password):
            # Set session variables
            session['user_id'] = staff.id
            session['user_name'] = f"{staff.first_name} {staff.last_name}"
            session['user_role'] = staff.role
            session['expiry'] = (datetime.now() + timedelta(hours=3)).isoformat()
            
            log_action('LOGIN', f'User logged in: {staff.full_name} ({staff.role})', staff.id)
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('/dashboard')  # Direct URL to avoid circular redirects
        else:
            flash('Invalid phone number or password', 'error')
    
    return render_template('login.html')

@auth.route('/logout')
def logout():
    if 'user_id' in session:
        log_action('LOGOUT', f'User logged out', session['user_id'])
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.login'))