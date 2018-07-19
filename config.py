"""Application configuration options"""

import datetime
import os


class Config:
    """Parent config class"""

    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    JWT_TOKEN_LOCATION = ['headers', 'query_string']
    JWT_QUERY_STRING_NAME = 'token'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    ADMIN = ['jomo@user.com']
    BOOK_RETURN_PERIOD = 14  # days
    DOMAIN = 'http://127.0.0.1:5000'

    # mail configuration
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_SENDER')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USER')
    MAIL_PASSWORD = os.environ.get('MAIL_PASS')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configurations"""

    DEBUG = True


class TestingConfig(Config):
    """Testing configurations"""

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/test_db'


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
