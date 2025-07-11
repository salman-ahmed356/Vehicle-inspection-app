import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask

from .database import db, migrate
from .models import (
    Address, Agent, Appointment, Branch, Company, Customer, Package,
    Report, Staff, Vehicle, VehicleOwner, ExpertiseType,
    ExpertiseFeature, ExpertiseReport, PackageExpertise
)
from .services.commands import register_commands
from .services.expertise_initializer import ExpertiseInitializer
from .tests.test_config import TestConfig
from .services.company_service import create_default_company
from .services.package_service import create_default_package

# Blueprints
from .routes.appointments import appointments as appointments_bp
from .routes.customers import customers as customers_bp
from .routes.reports import reports as reports_bp
from .routes.staffs import staff as staff_bp
from .routes.main import main as main_bp
from .routes.branches import branches as branches_bp
from .routes.companies import companies as companies_bp
from .routes.errors import errors as errors_bp
from .routes.packages import packages as packages_bp
from .routes.pdfs import pdfs as pdfs_bp


def create_app(config_object=None):
    # 1) Load .env into os.environ
    load_dotenv()

    # 2) Create Flask app
    app = Flask(
        __name__,
        static_url_path='/static',
        static_folder='static'
    )

    # 3) Configuration
    if config_object == 'testing':
        app.config.from_object(TestConfig)
        app.logger.setLevel(logging.DEBUG)
    else:
        # Base config (you can also move these defaults into config.Config)
        app.config['SECRET_KEY'] = os.getenv(
            'SECRET_KEY',
            'fallback-secret-key'
        )
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL',
            'sqlite:///data.db'
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Logging
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/error.log',
            maxBytes=10_240,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        app.logger.addHandler(stream_handler)

    # Suppress noisy fontTools subset logs
    logging.getLogger('fontTools.subset').setLevel(logging.WARNING)

    # 4) Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # 5) Register CLI commands
    register_commands(app)

    # 6) App context for startup tasks (migrations should be run separately)
    with app.app_context():
        ExpertiseInitializer.initialize_expertise_reports()
        create_default_company()
        create_default_package()

    # 7) Register blueprints
    app.register_blueprint(pdfs_bp)
    app.register_blueprint(packages_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(branches_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(main_bp)

    return app
