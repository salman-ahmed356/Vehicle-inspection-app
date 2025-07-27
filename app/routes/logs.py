from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from ..database import db
from ..models.system_log import SystemLog
from ..services.log_service import get_logs, delete_log, log_action
from ..rbac import role_required

logs = Blueprint('logs', __name__)

@logs.route('/logs')
@role_required('admin')
def system_logs():
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '')
    
    pagination = get_logs(page=page, per_page=50, search_term=search_term)
    
    return render_template(
        'logs/system_logs.html',
        logs=pagination.items,
        pagination=pagination,
        search_term=search_term
    )

@logs.route('/logs/delete/<int:log_id>', methods=['POST'])
@role_required('admin')
def delete_log_entry(log_id):
    if delete_log(log_id):
        log_action('LOG_DELETED', f'Deleted log entry ID: {log_id}')
        flash('Log entry deleted successfully.', 'success')
    else:
        flash('Error deleting log entry.', 'error')
    
    return redirect(url_for('logs.system_logs'))

@logs.route('/logs/delete-all', methods=['POST'])
@role_required('admin')
def delete_all_logs():
    try:
        SystemLog.query.delete()
        db.session.commit()
        log_action('LOGS_CLEARED', 'All system logs deleted')
        flash('All log entries deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting all logs.', 'error')
    
    return redirect(url_for('logs.system_logs'))

@logs.route('/logs/search')
@role_required('admin')
def search_logs():
    search_term = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    pagination = get_logs(page=page, per_page=50, search_term=search_term)
    
    return render_template(
        'logs/system_logs.html',
        logs=pagination.items,
        pagination=pagination,
        search_term=search_term
    )