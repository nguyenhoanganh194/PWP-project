import json
from jsonschema import FormatChecker, validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from playlistmanager.models import Playlist
from playlistmanager import db
from playlistmanager.utils import RespondBodyBuilder, create_error_response, is_validate_access_playlist
from playlistmanager.constants import *


class PlaylistCollection(Resource):
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
        body.add_control("self", url_for("api.playlistcollection", user=user))
        body.add_control_add_playlist(user)
        body["items"] = []
        for playlist in user.playlists:
            item = RespondBodyBuilder()
            item.add_control("self", url_for("api.playlistitem", user=user ,playlist=playlist))
            item.add_control("profile", PLAYLIST_PROFILE)
            body["items"].append(item)
        return Response(json.dumps(body), 200, mimetype=MASON)

    def post(self, user):
        """
        TODO: Write information for this
        """

        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")

        try:
            validate(request.json, Playlist.get_schema(),format_checker=FormatChecker())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

       
        playlist = Playlist()
        playlist.deserialize(request.json)
        playlist.user = user
        db.session.add(playlist)
        db.session.commit()
        return Response(status=201, 
                        headers={"Location": url_for("api.playlistitem", user=user, playlist = playlist)})       
    
                                        

class PlaylistItem(Resource):
    """
    TODO: Write information for this
    """

    def get(self, user, playlist):
        """
        TODO: Write information for this
        """
        if not is_validate_access_playlist(user,playlist):
            return create_error_response(409, "Not allow", "User not own playlist")
    
        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.playlistitem", user=user, playlist = playlist))
        body.add_control("profile", PLAYLIST_PROFILE)
        body.add_control("collection", url_for("api.playlistcollection", user = user))
        body.add_control_edit_playlist(user,playlist)
        body.add_control_delete(url_for("api.playlistitem", user=user, playlist=playlist))
        body.add_control_playlist_tracks(user,playlist)
        body["item"] = playlist.serialize()
        return Response(json.dumps(body), 200, mimetype=MASON)

    def put(self,  user, playlist):
        """
        TODO: Write information for this
        """

        status = 204
        if not request.json:
            return create_error_response(415, "Unsupported media type", "Requests must be JSON")
        try:
            validate(request.json, Playlist.get_schema(),format_checker=FormatChecker())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        if not is_validate_access_playlist(user,playlist):
            return create_error_response(409, "Not allow", "User not own playlist")

        status = 301
        playlist.deserialize(request.json)
        db.session.commit()
        headers = {"Location": url_for("api.playlistitem", user = user, playlist = playlist)}
        return Response(status=status, headers=headers)
    
    def delete(self, user, playlist):
        """
        TODO: Write information for this
        """
        if not is_validate_access_playlist(user,playlist):
            return create_error_response(409, "Not allow", "User not own playlist")
       
        db.session.delete(playlist)
        db.session.commit()
        return Response(status=204)
  

