import json
import secrets
from flask import Response, request, url_for
from playlistmanager.constants import *
from playlistmanager.models import *
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound, Forbidden

def create_error_response(status_code, title, message=None):
    resource_url = request.path
    body = MasonBuilder(resource_url=resource_url)
    body.add_error(title, message)
    body.add_control("profile", href=ERROR_PROFILE)
    return Response(json.dumps(body), status_code, mimetype=MASON)


class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.
        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.
        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.
        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.
        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md
        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href


class RespondBodyBuilder(MasonBuilder):
    """
    A subclass to build application specific Mason objects.
    """
#region User
    def add_control_users_all(self):
        """
        Adds users-all control, which leads to the users collection.
        """

        self.add_control(
            NAMESPACE_SHORT + ":users-all",
            href=url_for("api.usercollection"),
            method="GET",
            title="List all users"
        )
    def add_control_add_user(self):
        """
        Adds add-user control, which is used to add a user into the users collection.
        """

        self.add_control(
            NAMESPACE_SHORT + ":add-user",
            href=url_for("api.usercollection"),
            method="POST",
            encoding="json",
            title="Add a new player",
            schema=User.get_schema()
        )

    def add_control_edit_user(self, user):
        """
        Adds edit control, which is used to edit user item.
        : param str user: user's user_name
        """

        self.add_control(
            NAMESPACE_SHORT + ":edit-user",
            url_for("api.useritem", user=user),
            method="PUT",
            encoding="json",
            title="Edit this user",
            schema=User.get_schema()
        )
   
#endregion
    
#region Track
    def add_control_tracks(self , user):
        """
        TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":tracks-of",
            href=url_for("api.trackcollection", user = user),
            method="GET",
            title="List track of users"
        )
    def add_control_add_track(self, user):
        """
        TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":add-track",
            href=url_for("api.trackcollection", user = user),
            method="POST",
            encoding="json",
            title="Add a new track",
            schema=Track.get_schema()
        )

    def add_control_edit_track(self, user, track):
        """
           TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":edit-track",
            url_for("api.trackitem", user=user, track = track),
            method="PUT",
            encoding="json",
            title="Edit this track",
            schema=Track.get_schema()
        )
#endregion

#region Playlist
    def add_control_playlists(self , user):
        """
        TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":playlists-of",
            href=url_for("api.playlistcollection", user = user),
            method="GET",
            title="List playlists of users"
        )
    def add_control_add_playlist(self, user):
        """
        TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":add-playlist",
            href=url_for("api.playlistcollection", user = user),
            method="POST",
            encoding="json",
            title="Add a new playlist",
            schema=Playlist.get_schema()
        )

    def add_control_edit_playlist(self, user, playlist):
        """
           TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":edit-playlist",
            url_for("api.playlistitem", user=user, playlist = playlist),
            method="PUT",
            encoding="json",
            title="Edit this playlist",
            schema=Playlist.get_schema()
        )
#endregion

#region Playlist_track
    def add_control_playlist_tracks(self , user, playlist):
        """
        TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":tracks_of_playlist",
            href=url_for("api.playlisttrackcollection", user = user, playlist = playlist),
            method="GET",
            title="List tracks of playlist of user"
        )
    def add_control_add_playlist_track(self, user, playlist):
        """
        TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":add-playlisttrack",
            href=url_for("api.playlisttrackcollection",user = user, playlist = playlist),
            method="POST",
            encoding="json",
            title="Add a new playlisttrack to playlist",
            schema=PlaylistTrack.get_schema()
        )

    def add_control_edit_playlisttrack(self, user, playlist, playlist_track):
        """
           TODO: fill description for this
        """

        self.add_control(
            NAMESPACE_SHORT + ":edit-playlisttrack",
            url_for("api.playlisttrackitem", user=user, playlist = playlist, playlist_track = playlist_track),
            method="PUT",
            encoding="json",
            title="Edit this playlist",
            schema=PlaylistTrack.get_schema()
        )
#endregion

    def add_control_delete(self, href):
        """
        A generic delete function which should work for all resource types.
        : param str href: Resource's URI
        """

        self.add_control(
            NAMESPACE_SHORT + ":delete",
            href=href,
            method="DELETE",
            title="Delete this resource"
        )

def is_validate_access_playlist(user , playlist):
    try:
        if playlist not in user.playlists:
            return False
        return True
    except:
        return False
    

def is_validate_access_track(user , track):
    try:
        if track not in user.tracks:
            return False
        return True
    except:
        return False

def is_validate_access_playlist_track(user , playlist , playlist_track):
    if not is_validate_access_playlist(user,playlist):
        return False
    try:
        if playlist_track not in playlist.playlist_tracks:
            return False
        return True
    except:
        return False
    
def require_admin(func):
    def wrapper(*args, **kwargs):
        try:
            key_hash = AuthenticateKey.key_hash(request.headers.get("authenticate_key").strip())
            db_key = AuthenticateKey.query.filter_by(admin=True).first()
            if secrets.compare_digest(key_hash, db_key.key):
                return func(*args, **kwargs)
            else:
                raise Forbidden
        except:
            raise Forbidden
    return wrapper

def require_user_key(func):
    def wrapper(self, user, *args, **kwargs):
        try:
            key_hash = AuthenticateKey.key_hash(request.headers.get("authenticate_key").strip())
            db_key = AuthenticateKey.query.filter_by(user=user).first()
            if secrets.compare_digest(key_hash, db_key.key):
                return func(self, user,*args, **kwargs)
            else:
                raise Forbidden
        except Exception as e:
            raise Forbidden
    return wrapper
