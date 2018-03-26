class Config:
    """Parent config class"""
    DEBUG = False
    SECRET_KEY = '!!@#YDGGJGJGKJasdfadsff12526263JGKJH&*&^**IGHBJHB'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Configurations for development"""
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
