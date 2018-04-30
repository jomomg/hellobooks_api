"""Application configuration options"""

import datetime


class Config:
    """Parent config class"""

    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = '!!@#YDGGJGJGKJasdfadsff12526263JGKJH&*&^**IGHBJHB'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    SQLALCHEMY_DATABASE_URI = 'postgresql:///hellobooks_api'
    ADMIN = ['overlord@hellobooks.api']
    BOOK_RETURN_PERIOD = 14  # days

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
    SQLALCHEMY_DATABASE_URI = 'postgresql:///test_db'


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
