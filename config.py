import os
from datetime import timedelta

class Config:
    # MongoDB configuration - use environment variables for production
    MONGODB_HOST = os.environ.get('MONGODB_HOST') or 'localhost'
    MONGODB_PORT = int(os.environ.get('MONGODB_PORT') or 27017)
    MONGODB_DATABASE = os.environ.get('MONGODB_DATABASE') or 'agri_connect_db'
    MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME')
    MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
    
    # MongoDB connection URI
    # For production, you should use MongoDB Atlas connection string
    MONGODB_URI = os.environ.get('MONGODB_URI')
    if not MONGODB_URI:
        if MONGODB_USERNAME and MONGODB_PASSWORD:
            MONGODB_URI = f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DATABASE}'
        else:
            MONGODB_URI = f'mongodb://{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DATABASE}'
    
    # MongoDB settings for MongoEngine
    MONGODB_SETTINGS = {
        'host': MONGODB_URI,
        'connect': False  # Disable connection pooling for better compatibility with Flask
    }
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this-in-production'
    
    # File upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
