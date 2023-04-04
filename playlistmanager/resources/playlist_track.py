import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from playlistmanager.models import PlaylistTrack, Track, Playlist
from playlistmanager import db
from playlistmanager.utils import RespondBodyBuilder, create_error_response, is_validate_access_playlist_track, is_validate_access_playlist, is_validate_access_track
from playlistmanager.constants import *


class PlaylistTrackCollection(Resource):
    """
    The PlaylistTrackCollection resource supports GET and POST methods.
    Possible response codes:
    200 with a successful GET
    201 with a successful POST
    400 if JSON validating fails
    409 if item exists already
    415 if request is not JSON
    """

    def get(self, user, playlist):
        """
        GET method for the PlaylistTrackCollection. Lists user playlist track in the play list.
        : param user: user model
        : param playlist: playlist model
        """
        if not is_validate_access_playlist(user,playlist):
            return create_error_response(409, "Not allow", "User not own playlist")
    
        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.playlisttrackcollection",user=user ,playlist=playlist))
        body.add_control_add_playlist_track(user=user,playlist=playlist)
        body["items"] = []
        for playlist_track in playlist.playlist_tracks:
            item = RespondBodyBuilder()
            item.add_control("self", url_for("api.playlisttrackitem", user=user ,playlist=playlist, playlist_track = playlist_track))
            item.add_control("profile", PLAYLIST_TRACK_PROFILE)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user, playlist):
        """
        POST method for the PlaylistTrackCollection. Add new playlisttrack to a playlist
        : param user: user model
        : param playlist: playlist model
        """
        if not is_validate_access_playlist(user,playlist):
            return create_error_response(409, "Not allow", "User not own playlist")

        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, PlaylistTrack.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

   
        track = Track.query.filter_by(id=request.json["track_id"]).first()
        if not is_validate_access_track(user,track):
            return create_error_response(409, "Not allow", "User not own track")

        playlist_track = PlaylistTrack()
        playlist_track.deserialize(request.json)
        playlist_track.playlist = playlist
        playlist_track.track = track
        db.session.add(playlist_track)
        db.session.commit()
        return Response(status=201, 
                        headers={"Location": url_for("api.playlisttrackitem", user=user, playlist = playlist, playlist_track = playlist_track)})       
       
                                        

class PlaylistTrackItem(Resource):
    """
    The PlaylistTrackItem resource supports GET, PUT, and DELETE methods.
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

    def get(self, user, playlist, playlist_track):
        """
        GET method for the PlaylistTrackItem. Get a playlisttrack details information
        : param user: user model
        : param playlist: playlist model
        : param playlist_track: playlist_track model
        """
        if not is_validate_access_playlist_track(user,playlist,playlist_track):
            return create_error_response(409, "Not allow", "User not own playlist track")
    
        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.playlisttrackitem", user=user, playlist = playlist, playlist_track = playlist_track))
        body.add_control("profile", PLAYLIST_TRACK_PROFILE)
        body.add_control("collection", url_for("api.playlisttrackcollection", user = user, playlist = playlist))
        body.add_control_edit_playlisttrack(user,playlist,playlist_track)
        body.add_control_delete(url_for("api.playlisttrackitem", user=user, playlist=playlist, playlist_track = playlist_track))

        track = Track.query.filter_by(id=playlist_track.track_id).first()
        body.add_control("track", url_for("api.trackitem", user=user, track = track))
        body["item"] = playlist_track.serialize()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self, user, playlist, playlist_track):
        """
        PUT method for the PlaylistTrackItem. Edit a playlisttrack details information
        : param user: user model
        : param playlist: playlist model
        : param playlist_track: playlist_track model
        """

        status = 204
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")
        try:
            validate(request.json, PlaylistTrack.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        if not is_validate_access_playlist_track(user,playlist,playlist_track):
            return create_error_response(409, "Not allow", "User not own playlist track")

        status = 301
        track = Track.query.filter_by(id=request.json["track_id"]).first()
        playlist_track.deserialize(request.json)
        playlist_track.track = track
        db.session.commit()
        headers = {"Location": url_for("api.playlisttrackitem", user = user, playlist = playlist, playlist_track = playlist_track)}
        return Response(status=status, headers=headers)
   
    
    def delete(self, user, playlist, playlist_track):
        """
        DELETE method for the PlaylistTrackItem. Delete a playlisttrack from a playlist
        : param user: user model
        : param playlist: playlist model
        : param playlist_track: playlist_track model
        """
        if not is_validate_access_playlist_track(user,playlist, playlist_track):
            return create_error_response(409, "Not allow", "User not own playlist track")
 
        db.session.delete(playlist_track)
        db.session.commit()
        return Response(status=204)


