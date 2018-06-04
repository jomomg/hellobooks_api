"""Main application file"""

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from config import app_config

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()


def create_app(config_name):
    """Function for creating the application instance"""

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app_config[config_name].init_app(app)
    app.url_map.strict_slashes = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    @app.route('/')
    def home():
        """Return html containing link to documentation"""

        return app.send_static_file('/static/index.html')

    from app.auth import auth
    from app.main import main
    app.register_blueprint(auth)
    app.register_blueprint(main)
    return app
