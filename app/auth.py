from flask import session, redirect, url_for, request, flash
from datetime import datetime, timedelta
from functools import wraps

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or 'expiry' not in session:
            return redirect(url_for('auth.login', next=request.url))
        
        # Check if session has expired
        if datetime.now() > datetime.fromisoformat(session['expiry']):
            session.clear()
            flash('Your session has expired. Please login again.', 'error')
            return redirect(url_for('auth.login', next=request.url))
            
        # Extend session expiry on activity
        session['expiry'] = (datetime.now() + timedelta(hours=3)).isoformat()
        return f(*args, **kwargs)
    return decorated_function