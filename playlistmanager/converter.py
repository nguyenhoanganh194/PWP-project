
from playlistmanager.models import *
from werkzeug.routing import BaseConverter
from werkzeug.exceptions import NotFound
from playlistmanager.constants import *

class UserConverter(BaseConverter):
    """
    Converter for user resource
    """
    def to_python(self, value):
        user = User.query.filter_by(user_name=value).first()
        if user is None:
            raise NotFound
        return user

    def to_url(self, user):
        return str(user.user_name)
    

class TrackConverter(BaseConverter):
    """
    Converter for track resource
    """
    def to_python(self, value):
        track = Track.query.filter_by(id=value).first()
        if track is None:
            raise NotFound
        return track

    def to_url(self, track):
        return str(track.id)
    
class PlaylistConverter(BaseConverter):
    """
    Converter for playlist resource
    """
    def to_python(self, value):
        playlist = Playlist.query.filter_by(id=value).first()
        if playlist is None:
            raise NotFound
        return playlist

    def to_url(self, playlist):
        return str(playlist.id)