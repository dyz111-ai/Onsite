import os
from datetime import timedelta

class Config:
    # JWT 配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    UPLOAD_FOLDER = '../'
    ALLOWED_EXTENSIONS = {
        'open_scenario': {'xosc'},
        'target_points': {'json'}
    }
