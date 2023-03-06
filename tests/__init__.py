import os
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from resource.models import db
from resource.user import UsersResource

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="h3ll0",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    api = Api(app)
    api.add_resource(UsersResource, "/api/users/")
    db.init_app(app)
    with app.app_context():
        """
        Initializes a new database.
        """
        db.init_app(app)
        db.create_all()
    return app ,db
