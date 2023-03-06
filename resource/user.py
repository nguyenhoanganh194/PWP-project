import json
from flask import Response, request, url_for
from flask_restful import Resource
from jsonschema import validate, ValidationError

from resource.models import db
from resource.models import User

class UsersResource(Resource):
    def get(self, username = None):
        # Do get
        if(username is None):
            return create_respond(415,"Need username")
        entry = db.session.query(User).filter_by(user_name = username).first()
        if entry is None:
            return create_respond(404,"User not found")
        body = {
            "id": entry.id,
            "name": entry.user_name,
            "password": entry.password,
            "playlist": entry.playlists
        }
        return create_respond(200,"Successful", json.dumps(body))

    def post(self, username = None):
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

    def put(self, username, password):
        # I dont think we should implement this.
        pass

    def delete(self):
        # I dont think we should implement this.
        pass

def create_respond(status_code, title, message=None):
    #Create a respond here
    url = request.path
    body = {
        "tittle": title,
        "message": message
    }
    return Response(json.dumps(body), status_code)
