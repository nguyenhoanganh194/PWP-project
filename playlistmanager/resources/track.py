import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from playlistmanager.models import Track
from playlistmanager import db
from playlistmanager.utils import RespondBodyBuilder, create_error_response, is_validate_access_track
from playlistmanager.constants import *


class TrackCollection(Resource):
    """
    The TrackCollection resource supports ...
    TODO: Write information for this
    """

    def get(self, user):
        """
        TODO: Write information for this
        """
        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.trackcollection"))
        body.add_control_add_track()
        body["items"] = []
        for track in user.tracks:
            item = RespondBodyBuilder()
            item.add_control("self", url_for("api.trackitem", user=user ,track=track))
            item.add_control("profile", TRACK_PROFILE)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user):
        """
        TODO: Write information for this
        """

        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Track.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        try:
            track = Track()
            track.deserialize(request.json)
            track.user = user
            db.session.add(track)
            db.session.commit()
            return Response(status=201, 
                            headers={"Location": url_for("api.trackitem", user=user, track = track)})       
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))
                                        

class TrackItem(Resource):
    """
    TODO: Write information for this
    """

    def get(self, user, track):
        """
        TODO: Write information for this
        """
        if not is_validate_access_track(user,track):
            return create_error_response(409, "Not allow", "User not own track")
    
        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.trackitem", user=user, track = track))
        body.add_control("profile", TRACK_PROFILE)
        body.add_control("collection", url_for("api.trackcollection"), user = user)
        body.add_control_edit_track(user,track)
        body.add_control_delete(url_for("api.trackitem", user=user, track=track))

        body["item"] = track.serialize()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self,  user, track):
        """
        TODO: Write information for this
        """

        status = 204
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")
        try:
            validate(request.json, Track.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        if not is_validate_access_track(user,track):
            return create_error_response(409, "Not allow", "User not own track")

        try:
            status = 301
            track.deserialize(request.json)
            db.session.commit()
            headers = {"Location": url_for("api.trackitem", user = user, track = track)}
            return Response(status=status, headers=headers)
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))
    
    

    def delete(self, user, track):
        """
        TODO: Write information for this
        """
        if not is_validate_access_track(user,track):
            return create_error_response(409, "Not allow", "User not own track")
        try:
            db.session.delete(track)
            db.session.commit()
            return Response(status=204)
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))
    