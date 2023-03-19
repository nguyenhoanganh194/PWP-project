from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def get_schema_not_dedicate(self):
        return {
            "id": self.id,
            "username": self.username,
        }

    @staticmethod
    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string", "required": True},
                "password": {"type": "string", "required": True},
            }
        }


# Playlist model
# the Playlist model has a relationship with the User model using the user_id foreign key
class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)  # format: yyyy-mm-dd hh:mm:ss
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('playlists', lazy=True))

    def get_schema_not_dedicate(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
            "user": self.user.get_schema()
        }

    @staticmethod
    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "required": True},
                "created_at": {"type": "string", "format": "date-time", "required": True},
                "user_id": {"type": "integer", "required": True},
                "user": {"type": "object", "required": True, "properties": User.get_schema()['properties']}
            }
        }


# PlaylistTrack model
class PlaylistTrack(db.Model):
    __tablename__ = 'playlist_tracks'
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    playlist = db.relationship('Playlist', backref=db.backref('playlist_tracks', lazy=True))
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=False)
    track = db.relationship('Track', backref=db.backref('playlist_tracks', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('playlist_tracks', lazy=True))

    def get_schema_not_dedicate(self):
        return {
            "id": self.id,
            "playlist": self.playlist.get_schema(),
            "track": self.track.get_schema(),
            "user": self.user.get_schema()
        }

    @staticmethod
    def get_schema(self):
        return {
            'id': self.id,
            'playlist_id': self.playlist_id,
            'track_id': self.track_id,
            'user_id': self.user_id
        }


# Track model
class Track(db.Model):
    __tablename__ = 'tracks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    duration = db.Column(db.Integer, nullable=False)

    def get_schema_not_dedicate(self):
        return {
            "id": self.id,
            "name": self.name,
            "artist": self.artist,
            "duration": self.duration
        }

    @staticmethod
    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string", "required": True},
                "artist": {"type": "string", "required": True},
                "duration": {"type": "integer", "required": True}
            }
        }
