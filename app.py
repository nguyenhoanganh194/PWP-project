from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask.cli import with_appcontext
import resource.models as models
from resource.models import db
from resource.user import UsersResource
import random


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)
api.add_resource(UsersResource, "/users/")


with app.app_context():
    """
    Initializes a new database.
    """
    db.init_app(app)
    db.create_all()
    
