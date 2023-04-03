import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from playlistmanager.models import User
from playlistmanager import db
from playlistmanager.utils import RespondBodyBuilder, create_error_response, require_admin, require_user_key
from playlistmanager.constants import *


class UserCollection(Resource):
    """
    The UserCollection resource supports GET and POST methods.
    Possible response codes:
    200 with a successful GET
    201 with a successful POST
    400 if JSON validating fails
    409 if item exists already
    415 if request is not JSON
    """

    def get(self):
        """
        GET method for the User collection. Lists user items.
        """

        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.usercollection"))
        body.add_control_add_user()
        body["items"] = []
        for db_entry in User.query.all():
            item = RespondBodyBuilder()
            item.add_control("self", url_for("api.useritem", user=db_entry))
            item.add_control("profile", USER_PROFILE)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self):
        """
        POST method for the user collection. Adds a new user and includes the Location header
        in the response.
        """
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")
        try:
            validate(request.json, User.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))
        try:
            user = User()
            user.deserialize(request.json)
            db.session.add(user)
            db.session.commit()
            return Response(status=201, 
                            headers={"Location": url_for("api.useritem", user=user)})
        except IntegrityError:
            return create_error_response(409, "Already exists",
                                         "User '{}' already exists.".format(user.user_name))                                        

class UserItem(Resource):
    """
    The UserItem resource supports GET, PUT, and DELETE methods.
    Possible response codes:
    200 with a successful GET
    204 with a successful PUT or DELETE
    301 if item's location changes
    400 if JSON validating fails
    401 if invalid password
    404 if item was not found
    409 if item exists already
    415 if request is not JSON
    """

    def get(self, user):
        """
        GET method for the user item information.
        """

        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.useritem", user=user))
        body.add_control("profile", USER_PROFILE)
        body.add_control("collection", url_for("api.usercollection"))
        body.add_control_delete(url_for("api.useritem", user=user))
        body.add_control_edit_user(user)
        body.add_control_tracks(user)
        body.add_control_playlists(user)

        body["item"] = user.serialize()
        return Response(json.dumps(body), 200, mimetype=MASON)

    @require_user_key
    def put(self, user):
        """
        PUT method for editing the user. Includes the Location header. Requires api authentication.
        """

        status = 204
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")
        try:
            validate(request.json, User.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        try:
            new_user_name = request.json["user_name"]

            if user.user_name != new_user_name and User.query.filter_by(user_name=new_user_name).first():
                return create_error_response(409, "Already exists", "Username'{}' already exists.".format(new_user_name))

            if user.user_name != new_user_name:
                status = 301
                
            user.deserialize(request.json)
            headers = {"Location": url_for("api.useritem", user = user)}
            db.session.commit()
            return Response(status=status, headers=headers)
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))
    
    @require_user_key
    def delete(self, user):
        """
        DELETE method for the user item. Deletes the resource. Requires api authentication.
        """
        try:
            db.session.delete(user)
            db.session.commit()
            return Response(status=204)
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))