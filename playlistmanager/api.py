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
api.add_resource(UserCollection, "/users/")
api.add_resource(UserItem, "/users/<user:user>/")

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