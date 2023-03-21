
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="hello",
        SQLALCHEMY_DATABASE_URI="sqlite:///dev.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )


    with app.app_context():
        db.init_app(app)

    from . import api
    from . import models
    from .utils import UserConverter

    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.populate_db_command)
    app.url_map.converters["user"] = UserConverter
    app.register_blueprint(api.api_bp)

    return app