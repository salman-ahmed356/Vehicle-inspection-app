"""
Quick fix for static file serving issues with Cloudflare CDN
"""
from flask import Blueprint, send_from_directory, current_app, make_response
import os
import mimetypes

static_fix = Blueprint('static_fix', __name__)

@static_fix.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files with proper headers for Cloudflare"""
    try:
        # Get static folder path
        static_folder = current_app.static_folder
        if not static_folder:
            static_folder = os.path.join(current_app.root_path, 'static')
        
        # Create response
        response = make_response(send_from_directory(static_folder, filename))
        
        # Set proper MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if filename.endswith('.css'):
            mime_type = 'text/css'
        elif filename.endswith('.js'):
            mime_type = 'application/javascript'
        elif filename.endswith('.png'):
            mime_type = 'image/png'
        elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
            mime_type = 'image/jpeg'
        elif filename.endswith('.svg'):
            mime_type = 'image/svg+xml'
        
        if mime_type:
            response.headers['Content-Type'] = mime_type
        
        # Add cache headers
        response.headers['Cache-Control'] = 'public, max-age=3600'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Static file error: {e}")
        return "File not found", 404