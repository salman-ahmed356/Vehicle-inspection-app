from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = True
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Force English only
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_SUPPORTED_LOCALES = ['en']

    # Where to find your .po/.mo files
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
