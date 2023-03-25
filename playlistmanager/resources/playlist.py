import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from playlistmanager.models import Playlist
from playlistmanager import db
from playlistmanager.utils import RespondBodyBuilder, create_error_response
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
        body.add_control("self", url_for("api.playlistcollection"))
        body.add_control_add_playlist()
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
            validate(request.json, Playlist.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        try:
            playlist = Playlist()
            playlist.deserialize(request.json)
            playlist.user = user
            db.session.add(playlist)
            db.session.commit()
            return Response(status=201, 
                            headers={"Location": url_for("api.playlistitem", user=user, playlist = playlist)})       
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))
                                        

class PlaylistItem(Resource):
    """
    TODO: Write information for this
    """

    def get(self, user, playlist):
        """
        TODO: Write information for this
        """
        if not self.check_in_user(user,playlist):
            return create_error_response(409, "Not allow", "User not own playlist")
    
        body = RespondBodyBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", url_for("api.playlistitem", user=user, playlist = playlist))
        body.add_control("profile", PLAYLIST_PROFILE)
        body.add_control("collection", url_for("api.playlistcollection"), user = user)
        body.add_control_edit_playlist(user,playlist)
        body.add_control_delete(url_for("api.playlistitem", user=user, playlist=playlist))

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
            validate(request.json, Playlist.get_schema())
        except ValidationError as e:
            return create_error_response(400, "Invalid JSON document", str(e))

        if not self.check_in_user(user,playlist):
            return create_error_response(409, "Not allow", "User not own playlist")

        try:
            status = 301
            playlist.deserialize(request.json)
            db.session.commit()
            headers = {"Location": url_for("api.playlistitem", user = user, playlist = playlist)}
            return Response(status=status, headers=headers)
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))
    
    

    def delete(self, user, playlist):
        """
        TODO: Write information for this
        """
        if not self.check_in_user(user,playlist):
            return create_error_response(409, "Not allow", "User not own playlist")
        try:
            db.session.delete(playlist)
            db.session.commit()
            return Response(status=204)
        except Exception as e:
            return create_error_response(500, "Something's wrong.", str(e))


    def check_in_user(self, user , playlist):
        if playlist not in user.playlists:
            return False
        else:
            return True