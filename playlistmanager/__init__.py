
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="hello",
        SQLALCHEMY_DATABASE_URI="sqlite:///dev.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    with app.app_context():
        db.init_app(app)
        

    from . import api
    from . import models
    from .converter import UserConverter , TrackConverter, PlaylistConverter, PlaylistTrackConverter
    with app.app_context():
        db.create_all()
        
    app.cli.add_command(models.init_db_command)
    app.cli.add_command(models.populate_db_command)
    app.url_map.converters["user"] = UserConverter
    app.url_map.converters["track"] = TrackConverter
    app.url_map.converters["playlist"] = PlaylistConverter
    app.url_map.converters["playlist_track"] = PlaylistTrackConverter
    app.register_blueprint(api.api_bp)

    return app