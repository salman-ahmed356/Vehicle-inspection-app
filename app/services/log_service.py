from flask import session, request
from ..database import db
from ..models.system_log import SystemLog
from datetime import datetime, timedelta

def log_action(action, details=None, user_id=None):
    """Log a system action"""
    try:
        if not user_id:
            user_id = session.get('user_id')
        
        ip_address = request.remote_addr if request else None
        
        log_entry = SystemLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"Error logging action: {e}")
        db.session.rollback()

def get_logs(page=1, per_page=50, search_term=None):
    """Get system logs with pagination and search"""
    query = SystemLog.query
    
    if search_term:
        query = query.filter(
            db.or_(
                SystemLog.action.contains(search_term),
                SystemLog.details.contains(search_term)
            )
        )
    
    return query.order_by(SystemLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

def delete_log(log_id):
    """Delete a specific log entry"""
    try:
        log_entry = SystemLog.query.get(log_id)
        if log_entry:
            db.session.delete(log_entry)
            db.session.commit()
            return True
    except Exception as e:
        print(f"Error deleting log: {e}")
        db.session.rollback()
    return False

def clear_old_logs(days=30):
    """Clear logs older than specified days"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        old_logs = SystemLog.query.filter(SystemLog.timestamp < cutoff_date).all()
        
        for log in old_logs:
            db.session.delete(log)
        
        db.session.commit()
        return len(old_logs)
    except Exception as e:
        print(f"Error clearing old logs: {e}")
        db.session.rollback()
        return 0