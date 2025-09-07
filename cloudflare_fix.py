"""
Cloudflare CDN compatibility fixes for Flask application
"""
from flask import Flask, send_from_directory, make_response
import mimetypes
import os

def configure_cloudflare_compatibility(app: Flask):
    """Configure Flask app for Cloudflare CDN compatibility"""
    
    # Force HTTPS in production
    @app.before_request
    def force_https():
        from flask import request, redirect, url_for
        if not request.is_secure and app.env != 'development':
            return redirect(request.url.replace('http://', 'https://'))
    
    # Custom static file handler with proper MIME types
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve static files with correct MIME types for Cloudflare"""
        try:
            # Get the file path
            static_folder = app.static_folder or os.path.join(app.root_path, 'static')
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(filename)
            
            # Override specific MIME types for better Cloudflare compatibility
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
            
            # Create response
            response = make_response(send_from_directory(static_folder, filename))
            
            # Set proper headers for Cloudflare
            if mime_type:
                response.headers['Content-Type'] = mime_type
            
            # Cache control headers
            if filename.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.svg')):
                response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            
            # Security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            
            return response
            
        except Exception as e:
            app.logger.error(f"Error serving static file {filename}: {e}")
            return "File not found", 404
    
    # Add CSP header for external resources
    @app.after_request
    def add_security_headers(response):
        # Content Security Policy to allow CDN resources
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.tailwindcss.com; "
            "font-src 'self' https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )
        response.headers['Content-Security-Policy'] = csp
        
        # Additional headers for Cloudflare compatibility
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response