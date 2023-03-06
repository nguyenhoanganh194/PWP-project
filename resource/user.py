import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError
from app import db
from models import User
class UsersResource(Resource):
    def get(self):
        # Do get
        body =[]
        
        for entry in User.query.all():
            data = {
                "name": entry.name,
                "password": entry.password
            }

        pass

    def post(self):
        # Do post
        if not request.json:
            return create_respond(415, "Unsupported media type", "Requests must be JSON")
        try:
            validate(request.json, User.get_schema())
        except ValidationError as error:
            return create_respond(400,"Invalid json user",error)
        user = User()
        user.user_name = request.json["user_name"]
        user.password = request.json["password"]

        try:
            db.session.add(user)
            db.session.commit()
        except:
            return create_respond(400,"Can not add users")
        return create_respond(201, "Successful")
        pass

    def put(self, username, password):
        # I dont think we should implement this.
        pass

    def delete(self):
        # I dont think we should implement this.
        pass

def create_respond(status_code, title, message=None):
    #Create a respond here
    return ""