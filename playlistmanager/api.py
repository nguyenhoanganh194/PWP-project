from flask import Blueprint
from flask_restful import Api
from sqlalchemy import event
from sqlalchemy.engine import Engine
import json
from playlistmanager.resources.user import *
from playlistmanager.resources.playlist import *
from playlistmanager.resources.playlist_track import *
from playlistmanager.resources.track import *
from playlistmanager.constants import *
from playlistmanager.utils import RespondBodyBuilder
from flask import Response, redirect

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)
# Resources:
api.add_resource(UserCollection, "/user/")
api.add_resource(UserItem, "/user/<user:user>/")

api.add_resource(TrackCollection, "/track/<user:user>")
api.add_resource(TrackItem, "/track/<user:user>/<track:track>")

api.add_resource(PlaylistCollection, "/playlist/<user:user>")
api.add_resource(PlaylistItem, "/playlist/<user:user>/<playlist:playlist>")

api.add_resource(PlaylistTrackCollection, "/playlist_track/<user:user>/<playlist:playlist>")
api.add_resource(PlaylistTrackItem, "/playlist_track/<user:user>/<playlist:playlist>/<playlist_track:playlist_track>")


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Entry point:
@api_bp.route("/")
def entry_point():
    body = RespondBodyBuilder()
    body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
    body.add_control_users_all()
    return Response(json.dumps(body), 200, mimetype=MASON)