from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = True

    # ─── Flask-Babel CONFIG ───────────────────────────────────────────────────
    # Default language
    BABEL_DEFAULT_LOCALE = 'en'

    # List all supported locales
    BABEL_SUPPORTED_LOCALES = ['en', 'tr']

    # Where to find your .po/.mo files
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
