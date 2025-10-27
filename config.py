from app_secrets import MAIL_USERNAME, MAIL_PASSWORD, SECRET_KEY
import os
class Config:
    #Security
    SECRET_KEY = SECRET_KEY

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///redlight.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = MAIL_USERNAME
    MAIL_PASSWORD = MAIL_PASSWORD
    MAIL_ENABLED = False  

    # Uploads
    CAROUSSEL = 'website/caroussel'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 2000 * 1024 * 1024  # 2000MB max upload
    ALLOWED_EXTENSIONS = frozenset(['png', 'jpg', 'jpeg', 'gif'])

    # Flash categories customization 
    MESSAGE_CATEGORIES = {
        'error': 'danger',
        'message': 'info',
        'success': 'success'
    }

    # Logging
    LOG_TO_FILE = True
    LOG_FILE_PATH = 'logs/app.log'

    
