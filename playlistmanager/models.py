from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
import click

db = SQLAlchemy()

class User(db.Model):
    """
    User is the root model of the API, playlists, tracks are under it in the hierarchy.
    Each user will have a unique name and optional additional information.
    "user_name" is unique name, can be used to search user.
    "password" should be an MD5 checksum string of user's real password.
    "playlists" TODO fill
    "tracks" TODO fill
    """
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    user_name  = db.Column(db.String(64), nullable=False, unique=True)
    password  = db.Column(db.String(64), nullable=False)

    playlists = db.relationship("Playlist", cascade="all, delete-orphan", back_populates="user")
    tracks = db.relationship("Track", cascade="all, delete-orphan", back_populates="user")
    def serialize(self):
        playlists_serialize = []
        for entry in self.playlists:
            playlists_serialize.append(entry.serialize())

        track_serialize = []
        for entry in self.tracks:
            track_serialize.append(entry.serialize())
        return {
            "user_name": self.user_name, 
            "password": self.password,
            "playlists": playlists_serialize,
            "song": track_serialize
        }
    
    def deserialize(self, doc):
        self.user_name = doc["user_name"]
        self.password = doc["password"]


    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["user_name", "password"]
        }
        props = schema["properties"] = {}
        props["user_name"] = {
            "description": "User's name",
            "type": "string",
            "pattern": "^[a-z0-9_]{1,64}$"
        }
        props["password"] = {
            "description": "User's password",
            "type": "string",
            "pattern": "^[a-fA-F0-9]{64}$"
        }
        
        return schema

# Playlist model
# the Playlist model has a relationship with the User model using the user_id foreign key
class Playlist(db.Model):
    """
    The Playlist model defines a playlist of the API.
    "name" has to be alphanumeric string that can contain spaces, but no other special chars.
    TODO: fill description for each fields.
    "created_at" is ...
    """

    __tablename__ = 'playlist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)  # format: yyyy-mm-dd hh:mm:ss
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
      
    user = db.relationship('user', back_populates = "playlists")
    playlist_tracks = db.relationship("playlist_track", cascade="all, delete-orphan", back_populates="playlist")
    #TODO:add track in playlist relation ship
    def serialize(self):
        track_serialize = []
        for track in self.tracks:
            track_serialize.append(track.serialize())

        return {
            "id": self.id,
            "name": self.name, 
            "created_at": datetime.isoformat(self.created_at),
            "user": self.user.serialize(),
            "track": track_serialize
        }
    
    def deserialize(self, doc):
        self.name = doc["name"]
        self.created_at = datetime.fromisoformat(str(doc["created_at"]))


    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "created_at"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Playlist name",
            "type": "string",
            "pattern": "^[a-z0-9_]{1,64}$"
        }
        props["created_at"] = {
            "description": "Date time created",
            "type": "string",
            "format": "date-time"
        }
        return schema



# Track model
class Track(db.Model):
    """
    The Track model defines a Track of the API.
    TODO: fill description for each fields.
    """

    __tablename__ = 'track'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    artist = db.Column(db.String(80), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    user = db.relationship('User', back_populates = "tracks")
    playlist_tracks = db.relationship("playlist_track", cascade="all, delete-orphan", back_populates="track")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name, 
            "artist": self.artist,
            "duration": self.duration,
            "user": self.user.serialize()
        }
    
    def deserialize(self, doc):
        self.name = doc["name"]
        self.artist = doc["artist"]
        self.duration = doc["duration"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["name", "artist","duration"]
        }
        props = schema["properties"] = {}
        props["name"] = {
            "description": "Track name",
            "type": "string",
            "pattern": "^[a-z0-9_]{1,64}$"
        }
        props["artist"] = {
            "description": "Artist name",
            "type": "string",
            "pattern": "^[a-z0-9_]{1,64}$"
        }
        props["duration"] = {
            "description": "Duration",
            "type": "number",
        }
        return schema

# PlaylistTrack model
class PlaylistTrack(db.Model):
    """
    The PlaylistTrack model defines a PlaylistTrack of the API.
    TODO: fill description for each fields.
    """

    __tablename__ = 'playlist_track'
    id = db.Column(db.Integer, primary_key=True)

    track_number = db.Column(db.Integer, nullable=False, unique=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=False)

    playlist = db.relationship('playlist', backref=db.backref('playlist_tracks', lazy=True))
    track = db.relationship('track', backref=db.backref('playlist_tracks', lazy=True))

    def serialize(self):
        return {
            "id": self.id,
            "track_number": self.track_number, 
            "playlist": self.playlist.serialize(),
            "track": self.track.serialize(),
        }
    
    def deserialize(self, doc):
        self.track_number = doc["track_number"]

    @staticmethod
    def get_schema():
        schema = {
            "type": "object",
            "required": ["playlist_id", "track_id","track_number"]
        }
        props = schema["properties"] = {}
        props["playlist_id"] = {
            "description": "playlist_id",
            "type": "number",
        }
        props["track_id"] = {
            "description": "track_id",
            "type": "number",
        }
        props["track_number"] = {
            "description": "track_number",
            "type": "number",
        }
        return schema






@click.command("init-db")
@with_appcontext
def init_db_command():
    """
    Initializes a new database.
    """
    db.create_all()

@click.command("populate-db")
@with_appcontext
def populate_db_command():
    """
    Populates an initialized but empty database with some test values.
    raises IntegrityError: If the database contains the data already
    %Now only create user.
    raises OperationalError: If the database is not initialized
    """

    import hashlib
    from datetime import datetime
    from sqlalchemy.exc import IntegrityError, OperationalError
    try:
       
        u = {}
        for i in range(1, 4):
            u[i] = User(
                username="User {}".format(i),
                password="password{}".format(i),
            )
            db.session.add(u[i])
        db.session.commit()
    except IntegrityError:
        print("Failed to populate the database. Database must be empty.")
    except OperationalError:
        print("Failed to populate the database. Database must be initialized.")
