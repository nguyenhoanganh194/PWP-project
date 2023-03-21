from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(api_bp)

import json
from playlistmanager.resources.user import *
from playlistmanager.resources.playlist import *
from playlistmanager.resources.playlist_track import *
from playlistmanager.resources.song import *
from playlistmanager.constants import *
from playlistmanager.utils import ScoreBuilder
from flask import Response, redirect

# Resources:

api.add_resource(UserCollection, "/users/")
api.add_resource(UserItem, "/users/<user:user>/")


# Entry point:

@api_bp.route("/")
def entry_point():
    """
    Entry point has controls to go to list of all games or all users.
    """
    body = RespondBodyBuilder()
    body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
    body.add_control_users_all()
    return Response(json.dumps(body), 200, mimetype=MASON)