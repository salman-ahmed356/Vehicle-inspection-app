from flask import Blueprint, render_template, jsonify, current_app, request, redirect, url_for, flash
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from ..database import db

errors = Blueprint('errors', __name__)

# 413 Request Entity Too Large - Handle file upload size errors gracefully
@errors.app_errorhandler(413)
def error_413(error):
    # If this is a file upload error, redirect back with a user-friendly message
    if request.endpoint and 'report' in request.endpoint:
        flash('File is too large. Please try with a smaller file or contact support.', 'error')
        if 'edit_report' in request.endpoint:
            report_id = request.view_args.get('report_id')
            if report_id:
                return redirect(url_for('reports.edit_report', report_id=report_id))
        return redirect(url_for('reports.add_report'))
    
    # For other cases, show a generic error page
    return render_template('errors/400.html'), 413

# 404 Not Found
@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404

# 500 Internal Server Error
@errors.app_errorhandler(500)
def error_500(error):
    db.session.rollback()  # Rollback any failed database transactions
    return render_template('errors/500.html'), 500

# 403 Forbidden
@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403

# 400 Bad Request (Optional)
@errors.app_errorhandler(400)
def error_400(error):
    return render_template('errors/400.html'), 400


@errors.app_errorhandler(Exception)
def handle_exception(error):
    # If the error is an HTTPException, use its code
    if isinstance(error, HTTPException):
        return error_500(error)
    # Otherwise, return a 500 Internal Server Error
    current_app.logger.error(f'Unhandled Exception: {str(error)}')
    return render_template('errors/500.html'), 500
