"""
================================================================================
ENTERPRISE CONFIGURATION MANAGEMENT SYSTEM
System: Demulla IT Service Desk
Author: Engineer Mathias Alfred
Version: 3.0.0
Description: Advanced configuration management with environment-specific settings,
             security validation, and comprehensive feature flags for enterprise
             IT service management.
Features:
  - Multi-environment configuration management
  - Security validation and encryption
  - Feature flags and toggle management
  - Performance optimization settings
  - Comprehensive logging configuration
  - Third-party service integrations
  - Health check and monitoring settings
================================================================================
"""

import os
import re
from datetime import timedelta
from typing import Dict, Any, Optional
import logging
from urllib.parse import urlparse


class ConfigValidator:
    """
    Advanced configuration validation with security checks and integrity verification.
    Implements comprehensive validation rules for all configuration parameters.
    """
    
    @staticmethod
    def validate_database_url(url: str) -> bool:
        """
        Validate database URL format and security requirements.
        
        Args:
            url (str): Database connection URL
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValueError: If URL format is invalid or insecure
        """
        if not url:
            raise ValueError("Database URL cannot be empty")
        
        # Parse URL components
        parsed = urlparse(url)
        
        # Validate scheme
        valid_schemes = ['sqlite', 'postgresql', 'mysql', 'mariadb']
        if parsed.scheme not in valid_schemes:
            raise ValueError(f"Invalid database scheme. Must be one of: {valid_schemes}")
        
        # Security checks for production
        if parsed.scheme != 'sqlite':
            if not parsed.hostname:
                raise ValueError("Database hostname is required for non-SQLite databases")
            
            # Warn about localhost in production
            if os.getenv('FLASK_ENV') == 'production' and parsed.hostname in ['localhost', '127.0.0.1']:
                logging.warning("Using localhost database in production environment")
        
        return True
    
    @staticmethod
    def validate_secret_key(key: str) -> bool:
        """
        Validate secret key strength and complexity requirements.
        
        Args:
            key (str): Secret key to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValueError: If key doesn't meet security requirements
        """
        if not key or key == 'dev-secret-key-change-in-production':
            raise ValueError("Secret key must be set and different from default")
        
        if len(key) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        
        # Check for sufficient entropy
        entropy_requirements = {
            'uppercase': bool(re.search(r'[A-Z]', key)),
            'lowercase': bool(re.search(r'[a-z]', key)),
            'digits': bool(re.search(r'\d', key)),
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', key))
        }
        
        if sum(entropy_requirements.values()) < 3:
            raise ValueError("Secret key must include at least 3 character types (uppercase, lowercase, digits, special)")
        
        return True
    
    @staticmethod
    def validate_email_config(domain: str, api_key: str) -> bool:
        """
        Validate email service configuration parameters.
        
        Args:
            domain (str): Email service domain
            api_key (str): Email service API key
            
        Returns:
            bool: True if valid, False otherwise
        """
        if domain and not api_key:
            raise ValueError("Email API key required when domain is specified")
        
        if api_key and not domain:
            raise ValueError("Email domain required when API key is specified")
        
        if domain:
            # Basic domain format validation
            domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(domain_pattern, domain):
                raise ValueError("Invalid email domain format")
        
        return True


class SecurityConfig:
    """
    Comprehensive security configuration with best practices and hardening.
    Implements security headers, session management, and protection mechanisms.
    """
    
    # Session security
    SESSION_COOKIE_SECURE = True  # Only send over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    }
    
    # Password policy
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIREMENTS = {
        'uppercase': True,
        'lowercase': True,
        'digits': True,
        'special': True
    }
    
    # Rate limiting
    RATE_LIMIT_STORAGE_URL = 'memory://'  # Use Redis in production
    RATE_LIMIT_STRATEGY = 'fixed-window'
    RATE_LIMIT_DEFAULTS = {
        'per_minute': 60,
        'per_hour': 1000,
        'per_day': 10000
    }


class PerformanceConfig:
    """
    Performance optimization and caching configuration.
    Implements caching strategies, database optimization, and resource management.
    """
    
    # Database performance
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Caching configuration
    CACHE_TYPE = 'SimpleCache'  # Use Redis in production
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_THRESHOLD = 1000
    
    # Request timeout settings
    REQUEST_TIMEOUT = 30
    DATABASE_QUERY_TIMEOUT = 10
    
    # Static file optimization
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files
    STATIC_COMPRESSION = True


class MonitoringConfig:
    """
    Application monitoring, logging, and health check configuration.
    Implements comprehensive observability and alerting systems.
    """
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_MAX_BYTES = 10485760  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # Health check endpoints
    HEALTH_CHECK_ENDPOINTS = ['/health', '/ready', '/live']
    HEALTH_CHECK_TIMEOUT = 5
    
    # Metrics and analytics
    ENABLE_METRICS = True
    METRICS_ENDPOINT = '/metrics'
    ENABLE_ANALYTICS = True


class FeatureFlags:
    """
    Feature flag management for controlled rollouts and A/B testing.
    Enables gradual feature deployment and environment-specific functionality.
    """
    
    # Authentication features
    ENABLE_MFA = True
    ENABLE_SSO = False
    ENABLE_RECAPTCHA = True
    
    # Application features
    ENABLE_API_RATE_LIMITING = True
    ENABLE_ADVANCED_ANALYTICS = True
    ENABLE_REALTIME_NOTIFICATIONS = True
    ENABLE_AUTO_ASSIGNMENT = True
    
    # UI/UX features
    ENABLE_DARK_MODE = True
    ENABLE_ADVANCED_FILTERS = True
    ENABLE_BULK_OPERATIONS = True
    
    @classmethod
    def get_environment_flags(cls, environment: str) -> Dict[str, bool]:
        """
        Get feature flags specific to an environment.
        
        Args:
            environment (str): Target environment
            
        Returns:
            Dict[str, bool]: Environment-specific feature flags
        """
        base_flags = {k: v for k, v in cls.__dict__.items() 
                     if not k.startswith('_') and isinstance(v, bool)}
        
        environment_overrides = {
            'development': {
                'ENABLE_SSO': False,
                'ENABLE_RECAPTCHA': False,
                'ENABLE_API_RATE_LIMITING': False
            },
            'production': {
                'ENABLE_SSO': True,
                'ENABLE_RECAPTCHA': True,
                'ENABLE_API_RATE_LIMITING': True
            }
        }
        
        overrides = environment_overrides.get(environment, {})
        return {**base_flags, **overrides}


class BaseConfig:
    """
    Base configuration class with comprehensive enterprise settings.
    Implements validation, security, and performance best practices.
    """
    
    def __init__(self):
        """Initialize configuration with validation and security checks."""
        self._validator = ConfigValidator()
        self._validate_configuration()
    
    def _validate_configuration(self) -> None:
        """
        Validate all configuration parameters for security and integrity.
        
        Raises:
            ValueError: If any configuration parameter is invalid
        """
        try:
            # Database validation
            self._validator.validate_database_url(self.SQLALCHEMY_DATABASE_URI)
            
            # Security validation
            self._validator.validate_secret_key(self.SECRET_KEY)
            
            # Email service validation
            self._validator.validate_email_config(
                self.MAILGUN_DOMAIN, 
                self.MAILGUN_API_KEY
            )
            
            logging.info("✅ Configuration validation completed successfully")
            
        except ValueError as e:
            logging.error(f"❌ Configuration validation failed: {e}")
            raise
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    
    # Primary database connection
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///service_requests.db'
    
    # Database performance and connection management
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = PerformanceConfig.SQLALCHEMY_ENGINE_OPTIONS
    
    # Database connection pool settings
    SQLALCHEMY_POOL_RECYCLE = 300  # Recycle connections after 5 minutes
    SQLALCHEMY_POOL_TIMEOUT = 30   # Connection pool timeout
    SQLALCHEMY_MAX_OVERFLOW = 20   # Maximum overflow connections
    
    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    
    # Application secret key (override in production)
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'dev-secret-key-change-in-production-ensure-32-chars-min'
    
    # Session security settings
    SESSION_COOKIE_SECURE = SecurityConfig.SESSION_COOKIE_SECURE
    SESSION_COOKIE_HTTPONLY = SecurityConfig.SESSION_COOKIE_HTTPONLY
    SESSION_COOKIE_SAMESITE = SecurityConfig.SESSION_COOKIE_SAMESITE
    PERMANENT_SESSION_LIFETIME = SecurityConfig.PERMANENT_SESSION_LIFETIME
    
    # Security headers
    SECURITY_HEADERS = SecurityConfig.SECURITY_HEADERS
    
    # Password policy
    PASSWORD_MIN_LENGTH = SecurityConfig.PASSWORD_MIN_LENGTH
    PASSWORD_REQUIREMENTS = SecurityConfig.PASSWORD_REQUIREMENTS
    
    # Rate limiting
    RATE_LIMIT_STORAGE_URL = SecurityConfig.RATE_LIMIT_STORAGE_URL
    RATE_LIMIT_STRATEGY = SecurityConfig.RATE_LIMIT_STRATEGY
    RATE_LIMIT_DEFAULTS = SecurityConfig.RATE_LIMIT_DEFAULTS
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    
    # Application metadata
    APP_NAME = "Demulla IT Service Desk"
    APP_VERSION = "3.0.0"
    APP_DESCRIPTION = "Enterprise IT Service Request Tracking System"
    
    # Admin and support configuration
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@demulla.com'
    SUPPORT_EMAIL = os.environ.get('SUPPORT_EMAIL') or 'support@demulla.com'
    SYSTEM_FROM_EMAIL = os.environ.get('SYSTEM_FROM_EMAIL') or 'noreply@demulla.com'
    
    # Request limits and quotas
    MAX_REQUESTS_PER_USER = 1000
    MAX_FILE_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
    MAX_CONTENT_LENGTH = MAX_FILE_UPLOAD_SIZE
    
    # =============================================================================
    # THIRD-PARTY INTEGRATIONS
    # =============================================================================
    
    # Email service configuration (Mailgun)
    MAILGUN_DOMAIN = os.environ.get('MAILGUN_DOMAIN')
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY')
    
    # Monitoring and analytics (Sentry)
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    ENABLE_SENTRY = bool(SENTRY_DSN)
    
    # ReCAPTCHA configuration
    RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
    ENABLE_RECAPTCHA = bool(RECAPTCHA_SITE_KEY and RECAPTCHA_SECRET_KEY)
    
    # =============================================================================
    # PERFORMANCE AND CACHING
    # =============================================================================
    
    # Caching configuration
    CACHE_TYPE = PerformanceConfig.CACHE_TYPE
    CACHE_DEFAULT_TIMEOUT = PerformanceConfig.CACHE_DEFAULT_TIMEOUT
    CACHE_THRESHOLD = PerformanceConfig.CACHE_THRESHOLD
    
    # Request and query timeouts
    REQUEST_TIMEOUT = PerformanceConfig.REQUEST_TIMEOUT
    DATABASE_QUERY_TIMEOUT = PerformanceConfig.DATABASE_QUERY_TIMEOUT
    
    # Static file optimization
    SEND_FILE_MAX_AGE_DEFAULT = PerformanceConfig.SEND_FILE_MAX_AGE_DEFAULT
    STATIC_COMPRESSION = PerformanceConfig.STATIC_COMPRESSION
    
    # =============================================================================
    # MONITORING AND LOGGING
    # =============================================================================
    
    # Logging configuration
    LOG_LEVEL = MonitoringConfig.LOG_LEVEL
    LOG_FORMAT = MonitoringConfig.LOG_FORMAT
    LOG_MAX_BYTES = MonitoringConfig.LOG_MAX_BYTES
    LOG_BACKUP_COUNT = MonitoringConfig.LOG_BACKUP_COUNT
    
    # Health check configuration
    HEALTH_CHECK_ENDPOINTS = MonitoringConfig.HEALTH_CHECK_ENDPOINTS
    HEALTH_CHECK_TIMEOUT = MonitoringConfig.HEALTH_CHECK_TIMEOUT
    
    # Metrics configuration
    ENABLE_METRICS = MonitoringConfig.ENABLE_METRICS
    METRICS_ENDPOINT = MonitoringConfig.METRICS_ENDPOINT
    ENABLE_ANALYTICS = MonitoringConfig.ENABLE_ANALYTICS
    
    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    
    @property
    def FEATURE_FLAGS(self) -> Dict[str, bool]:
        """Get feature flags for current environment."""
        environment = os.environ.get('FLASK_ENV', 'development')
        return FeatureFlags.get_environment_flags(environment)


class DevelopmentConfig(BaseConfig):
    """
    Development environment configuration with debug settings and developer tools.
    Optimized for local development and testing.
    """
    
    # Debug and testing features
    DEBUG = True
    TESTING = False
    EXPLAIN_TEMPLATE_LOADING = False
    
    # Database configuration for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///service_requests_dev.db'
    
    # Development-specific security settings
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Enhanced logging for development
    LOG_LEVEL = 'DEBUG'
    SQLALCHEMY_ECHO = False  # Set to True for SQL query logging
    
    # Development feature flags
    ENABLE_DEBUG_TOOLBAR = True
    ENABLE_SQL_PROFILING = True
    
    def __init__(self):
        """Initialize development configuration with additional validations."""
        super().__init__()
        logging.info("🚀 Development configuration loaded with debug features")


class TestingConfig(BaseConfig):
    """
    Testing environment configuration for automated tests and CI/CD.
    Isolated database and optimized for test performance.
    """
    
    # Testing-specific settings
    TESTING = True
    DEBUG = False
    
    # Isolated test database
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'
    
    # Disable security features for testing
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    
    # Test performance optimization
    SQLALCHEMY_ECHO = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Testing feature flags
    ENABLE_RATE_LIMITING = False
    
    def __init__(self):
        """Initialize testing configuration with test-specific settings."""
        super().__init__()
        logging.info("🧪 Testing configuration loaded with isolated database")


class StagingConfig(BaseConfig):
    """
    Staging environment configuration for pre-production testing.
    Mirrors production settings with additional monitoring.
    """
    
    # Production-like settings
    DEBUG = False
    TESTING = False
    
    # Staging-specific database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///service_requests_staging.db'
    
    # Enhanced monitoring for staging
    LOG_LEVEL = 'INFO'
    ENABLE_SENTRY = True
    
    # Staging feature flags
    ENABLE_NEW_FEATURES = True  # Test new features in staging
    
    def __init__(self):
        """Initialize staging configuration with production-like settings."""
        super().__init__()
        logging.info("🔄 Staging configuration loaded with production settings")


class ProductionConfig(BaseConfig):
    """
    Production environment configuration with maximum security and performance.
    Optimized for scalability, security, and reliability.
    """
    
    # Production security settings
    DEBUG = False
    TESTING = False
    
    # Production database (must be set via environment variable)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is required for production")
    
    # Maximum security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Production performance optimization
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 20,
        'max_overflow': 30,
        'pool_timeout': 30
    }
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    LOG_MAX_BYTES = 50 * 1024 * 1024  # 50MB in production
    LOG_BACKUP_COUNT = 10
    
    # Production monitoring
    ENABLE_SENTRY = True
    ENABLE_METRICS = True
    
    def __init__(self):
        """Initialize production configuration with strict validations."""
        # Additional production validations
        if self.SECRET_KEY == 'dev-secret-key-change-in-production-ensure-32-chars-min':
            raise ValueError("SECRET_KEY must be set in production environment")
        
        if not self.MAILGUN_DOMAIN or not self.MAILGUN_API_KEY:
            logging.warning("Email notifications disabled: MAILGUN configuration missing")
        
        super().__init__()
        logging.info("🏭 Production configuration loaded with maximum security")


# =============================================================================
# CONFIGURATION REGISTRY AND MANAGEMENT
# =============================================================================

class ConfigManager:
    """
    Advanced configuration management with environment detection and validation.
    Provides centralized configuration access and management.
    """
    
    # Configuration registry
    _configs = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'staging': StagingConfig,
        'production': ProductionConfig
    }
    
    @classmethod
    def get_config(cls, environment: Optional[str] = None) -> BaseConfig:
        """
        Get configuration for specified environment with fallback detection.
        
        Args:
            environment (str, optional): Target environment. Auto-detected if None.
            
        Returns:
            BaseConfig: Configuration instance for the specified environment
            
        Raises:
            ValueError: If environment is invalid or configuration fails
        """
        # Auto-detect environment
        if not environment:
            environment = os.environ.get('FLASK_ENV', 'development')
        
        # Normalize environment name
        environment = environment.lower()
        
        # Get configuration class
        config_class = cls._configs.get(environment)
        if not config_class:
            raise ValueError(f"Invalid environment: {environment}. "
                           f"Must be one of: {list(cls._configs.keys())}")
        
        try:
            # Instantiate configuration
            config = config_class()
            logging.info(f"✅ Loaded {environment} configuration successfully")
            return config
            
        except Exception as e:
            logging.error(f"❌ Failed to load {environment} configuration: {e}")
            raise
    
    @classmethod
    def get_current_environment(cls) -> str:
        """
        Get current application environment.
        
        Returns:
            str: Current environment name
        """
        return os.environ.get('FLASK_ENV', 'development')
    
    @classmethod
    def is_production(cls) -> bool:
        """
        Check if current environment is production.
        
        Returns:
            bool: True if production environment
        """
        return cls.get_current_environment() == 'production'
    
    @classmethod
    def is_development(cls) -> bool:
        """
        Check if current environment is development.
        
        Returns:
            bool: True if development environment
        """
        return cls.get_current_environment() == 'development'


# =============================================================================
# CONFIGURATION EXPORTS AND COMPATIBILITY
# =============================================================================

# Configuration dictionary for Flask app initialization
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# Global configuration instance
def get_config() -> BaseConfig:
    """
    Get current configuration instance.
    
    Returns:
        BaseConfig: Current configuration instance
    """
    return ConfigManager.get_config()

# Export commonly used configuration checks
is_production = ConfigManager.is_production
is_development = ConfigManager.is_development
get_environment = ConfigManager.get_current_environment

# Export feature flags helper
def get_feature_flags() -> Dict[str, bool]:
    """
    Get current feature flags.
    
    Returns:
        Dict[str, bool]: Current feature flags
    """
    return get_config().FEATURE_FLAGS


# =============================================================================
# CONFIGURATION INITIALIZATION AND VALIDATION
# =============================================================================

if __name__ == '__main__':
    """
    Configuration validation and testing script.
    Run this module directly to validate configuration settings.
    """
    try:
        # Test configuration loading
        current_env = ConfigManager.get_current_environment()
        config_instance = ConfigManager.get_config(current_env)
        
        print(f"✅ Configuration validation successful for {current_env} environment")
        print(f"📊 Feature flags: {config_instance.FEATURE_FLAGS}")
        print(f"🔐 Security headers: {len(config_instance.SECURITY_HEADERS)} configured")
        print(f"🚀 Performance settings: Database pool size = {config_instance.SQLALCHEMY_ENGINE_OPTIONS.get('pool_size', 'default')}")
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        exit(1)