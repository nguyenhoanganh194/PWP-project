import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from playlistmanager.models import User
from playlistmanager import db
from playlistmanager.utils import RespondBodyBuilder, create_error_response
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
            item.add_control("self", url_for("api.useritem", user=db_entry.user_name))
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

        user = User()
        user.user_name = request.json["user_name"]
        user.password = request.json["password"]

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return create_error_response(409, "Already exists",
                                         "User '{}' already exists.".format(user.user_name)
                                         )

        return Response(status=201, headers={
            "Location": url_for("api.useritem", user=user.user_name)
        })


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

    def get(self, user_name):
        """
        GET method for the user item information.
        :param user_name: user's name
        """

        db_entry = User.query.filter_by(user_name=user_name).first()
        if db_entry is None:
            return create_error_response(404, "Not found", "Ulayer '{}' wasn't found.".format(user_name))

        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.useritem", user=user_name))
        body.add_control("profile", USER_PROFILE)
        body.add_control("collection", url_for("api.usercollection"))
        body.add_control_delete(url_for("api.useritem", user=user_name))
        body.add_control_edit_user(user_name)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, user_name):
        """
        PUT method for editing the user. Includes the Location header. Requires password authentication.
        :param user_name: User's current name
        """

        status = 204
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")
        try:
            validate(request.json, User.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        db_entry = User.query.filter_by(user_name=user_name).first()
        if db_entry is None:
            return create_error_response(404, "Not found", "User '{}' wasn't found.".format(user_name))

        new_user_name = request.json["user_name"].lower().replace(" ", "_")

        if db_entry.unique_name != new_user_name and User.query.filter_by(unique_name=new_user_name).first():
            return create_error_response(409, "Already exists", "User '{}' already exists.".format(new_user_name))

        if db_entry.password != request.json["password"]:
            return create_error_response(401, "Unauthorized", "Invalid password.")

        if db_entry.unique_name != new_user_name:
            status = 301
            headers = {"Location": url_for("api.useritem", user=new_user_name)}
        else:
            headers = None

        try:
            db_entry.user_name = request.json["user_name"]
            db_entry.password = request.json["password"]
            db.session.commit()
            return Response(status=status, headers=headers)
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))
    

    def delete(self, user):
        """
        DELETE method for the user item. Deletes the resource.
        :param user: user's name
        """

        db_entry = User.query.filter_by(user_name=user).first()
        if db_entry is None:
            return create_error_response(404, "Not found", "User wasn't found.")
        try:
            db.session.delete(db_entry)
            db.session.commit()
            return Response(status=204)
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))