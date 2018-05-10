from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from .api import api as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
