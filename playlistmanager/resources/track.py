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
    The TrackCollection resource supports GET and POST methods.
    Possible response codes:
    200 with a successful GET
    201 with a successful POST
    400 if JSON validating fails
    409 if item exists already
    415 if request is not JSON
    """

    def get(self, user):
        """
        GET method for the TrackCollection. Lists user tracks
        : param user: user model
        """
        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.trackcollection", user = user))
        body.add_control_add_track(user)
        body["items"] = []
        for track in user.tracks:
            item = RespondBodyBuilder()
            item.add_control("self", url_for("api.trackitem", user=user ,track=track))
            item.add_control("profile", TRACK_PROFILE)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user):
        """
        GET method for the TrackCollection. Add new track to user tracks
        : param user: user model
        """

        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Track.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        
        track = Track()
        track.deserialize(request.json)
        track.user = user
        db.session.add(track)
        db.session.commit()
        return Response(status=201, 
                        headers={"Location": url_for("api.trackitem", user=user, track = track)})       
        
                                        

class TrackItem(Resource):
    """
    The TrackItem resource supports GET, PUT, and DELETE methods.
    Possible response codes:
    200 with a successful GET
    204 with a successful PUT or DELETE
    301 if item's location changes
    400 if JSON validating fails
    404 if item was not found
    409 if item exists already
    415 if request is not JSON
    """

    def get(self, user, track):
        """
        GET method for the TrackItem.Get a TrackItem details information
        : param user: user model
        : param track: track model
        """
        if not is_validate_access_track(user,track):
            return create_error_response(409, "Not allow", "User not own track")
    
        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.trackitem", user=user, track = track))
        body.add_control("profile", TRACK_PROFILE)
        body.add_control("collection", url_for("api.trackcollection", user = user))
        body.add_control_edit_track(user,track)
        body.add_control_delete(url_for("api.trackitem", user=user, track=track))

        body["item"] = track.serialize()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self,  user, track):
        """
        PUT method for the TrackItem. Edit a TrackItem details information
        : param user: user model
        : param track: track model
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


        status = 301
        track.deserialize(request.json)
        db.session.commit()
        headers = {"Location": url_for("api.trackitem", user = user, track = track)}
        return Response(status=status, headers=headers)
       

    def delete(self, user, track):
        """
        PUT method for the TrackItem. Delete a TrackItem
        : param user: user model
        : param track: track model
        """
        if not is_validate_access_track(user,track):
            return create_error_response(409, "Not allow", "User not own track")

        db.session.delete(track)
        db.session.commit()
        return Response(status=204)

    