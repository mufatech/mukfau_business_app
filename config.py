# class Config:
#     DEBUG = True

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Required configurations
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Debug mode (default to False for safety)
    DEBUG = os.getenv('FLASK_DEBUG')
