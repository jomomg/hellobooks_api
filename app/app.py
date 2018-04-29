"""Main application file"""

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

from config import app_config

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_name):
    """Function for creating the application instance"""

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app_config[config_name].init_app(app)
    app.url_map.strict_slashes = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    jwt.init_app(app)

    from app.auth import auth
    from app.main import main
    app.register_blueprint(auth)
    app.register_blueprint(main)
    return app
