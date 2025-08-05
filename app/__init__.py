import os
from flask import Flask, request, session, redirect, url_for
from flask_babel import Babel
from flask_migrate import Migrate
from datetime import timedelta

from .database import db
from .auth import login_required
from .routes.main import main
from .routes.reports import reports
from .routes.pdfs import pdfs
from .routes.appointments import appointments
from .routes.companies import companies
from .routes.packages import packages
from .routes.customers import customers
from .routes.staffs import staff
from .routes.vehicles import vehicles
from .routes.report_settings import report_settings
from .routes.auth import auth
from .routes.api import api
from .routes.logs import logs

babel = Babel()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Redirect to login if not authenticated
    @app.route('/')
    def root():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return redirect('/dashboard')  # Direct URL to avoid circular redirects
    
    # Load configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///data.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        BABEL_DEFAULT_LOCALE='en',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=3),
    )
    
    # Make sessions permanent by default
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    babel.init_app(app)

    # Error handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        from flask import flash, redirect, request
        flash('Image file is too large. Please select a smaller image (max 5MB).', 'error')
        return redirect(request.referrer or url_for('reports.add_report'))
    
    @app.errorhandler(400)
    def bad_request(error):
        from flask import flash, redirect, request
        flash('Invalid file upload. Please try again with a different image.', 'error')
        return redirect(request.referrer or url_for('reports.add_report'))

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(reports)
    app.register_blueprint(pdfs)
    app.register_blueprint(appointments)
    app.register_blueprint(companies)
    app.register_blueprint(packages)
    app.register_blueprint(customers)
    app.register_blueprint(staff)
    app.register_blueprint(vehicles)
    app.register_blueprint(report_settings)
    app.register_blueprint(api)
    app.register_blueprint(logs)

    # Remove automatic table creation to avoid startup issues
    # Tables will be created manually after database is ready

    # Make get_locale available to templates
    @app.context_processor
    def inject_get_locale():
        return dict(get_locale=lambda: request.accept_languages.best_match(['en', 'tr']))

    return app