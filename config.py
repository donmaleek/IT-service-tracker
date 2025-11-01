"""
Configuration settings for the IT Service Request Tracking System.
Contains environment-specific settings and third-party API configurations.
"""
import os
from datetime import datetime

class Config:
    """
    Base configuration class with default settings for the application.
    """
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///service_requests.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Email configuration for notifications
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    
    # Application settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@company.com'

class DevelopmentConfig(Config):
    """
    Development environment configuration with debug settings enabled.
    """
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """
    Production environment configuration with secure settings.
    """
    DEBUG = False
    TESTING = False

# Configuration dictionary for easy environment switching
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}