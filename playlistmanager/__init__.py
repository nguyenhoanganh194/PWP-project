
import os
from flask import Flask, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

from playlistmanager.constants import *

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_folder="static")
    app.config.from_mapping(
        SECRET_KEY="hello",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "dev.db"),
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

    @app.route(LINK_RELATIONS_URL)
    def redirect_link_relations():
        return redirect(APIARY_URL + "link-relations")
    

    @app.route("/")
    def redirect_swagger_ui():
        return render_template('swaggerui.html')
    
    @app.route("/JsonYaml")
    def get_yaml_json():
        return render_template('swaggerui.html')
    
    
    @app.route("/profiles/<profile>/")
    def redirect_profiles(profile):
        return redirect(APIARY_URL + "profiles")
    
    return app