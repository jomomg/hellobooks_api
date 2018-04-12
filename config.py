"""Application configuration options"""

import datetime


class Config:
    """Parent config class"""

    DEBUG = False
    SECRET_KEY = '!!@#YDGGJGJGKJasdfadsff12526263JGKJH&*&^**IGHBJHB'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=60)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']

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

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
