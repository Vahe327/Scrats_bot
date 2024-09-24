import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///scrats_game.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_TOKEN = os.getenv('API_TOKEN', 'Token')
