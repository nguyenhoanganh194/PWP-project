import os
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from resource.models import db
from resource.user import UsersResource
from sqlalchemy import MetaData

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="h3ll0",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )
    api = Api(app)
    api.add_resource(UsersResource, "/api/users/<username>/")
    with app.app_context():
        db.init_app(app)
        db.create_all()
        meta = MetaData(bind=db.engine)
        meta.reflect()
        # Get a list of table names
        table_names = meta.tables.keys()
        print(table_names)
    return app ,db
