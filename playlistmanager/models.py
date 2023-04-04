from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from playlistmanager import db
from sqlalchemy import MetaData
import click
import hashlib


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
    api_key = db.relationship("AuthenticateKey", cascade="all, delete-orphan", back_populates="user")

    def serialize(self):
        return {
            "user_name": self.user_name
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
            # "pattern": "^(?=[a-zA-Z0-9._]{8,20}$)(?!.*[_.]{2})[^_.].*[^_.]$"
        }
        props["password"] = {
            "description": "User's password",
            "type": "string",
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
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)  # format: yyyy-mm-dd hh:mm:ss
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
      
    user = db.relationship('User', back_populates = "playlists")
    playlist_tracks = db.relationship("PlaylistTrack", cascade="all, delete-orphan", back_populates="playlist")
    #TODO:add track in playlist relation ship
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name, 
            "created_at": datetime.isoformat(self.created_at),
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
            "pattern": "^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$"
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
    playlist_tracks = db.relationship("PlaylistTrack", cascade="all, delete-orphan", back_populates="track")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name, 
            "artist": self.artist,
            "duration": self.duration,
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
            "pattern": "^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$"
        }
        props["artist"] = {
            "description": "Artist name",
            "type": "string",
            "pattern": "^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$"
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

    track_number = db.Column(db.Integer, nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    track_id = db.Column(db.Integer, db.ForeignKey('track.id'), nullable=False)

    playlist = db.relationship('Playlist', back_populates = "playlist_tracks")
    track = db.relationship('Track', back_populates = "playlist_tracks")

    def serialize(self):
        return {
            "id": self.id,
            "track_number": self.track_number, 
            "track_id":self.track_id,
            "playlist_id": self.playlist_id
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
        props["track_id"] = {
            "description": "track_id",
            "type": "number",
        }
        props["track_number"] = {
            "description": "track_number",
            "type": "number",
        }
        return schema

class AuthenticateKey(db.Model):
    """
    The PlaylistTrack model defines a PlaylistTrack of the API.
    TODO: fill description for each fields.
    """
    key = db.Column(db.String(32), nullable=False, unique=True,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    admin =  db.Column(db.Boolean, default=False)
     
    user = db.relationship('User', back_populates = "api_key", uselist=False)
    
    @staticmethod
    def key_hash(key):
        return hashlib.sha256(key.encode()).digest()
     




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
    raises OperationalError: If the database is not initialized
    """

    import secrets
    from datetime import datetime
    from sqlalchemy.exc import IntegrityError, OperationalError

    meta = MetaData()
    meta.reflect(db.engine)
    # Get a list of table names
    table_names = meta.tables.keys()
    print(table_names)

    token = secrets.token_urlsafe()
    db_key = AuthenticateKey(
        key= AuthenticateKey.key_hash(token),
        admin=True
    )
    db.session.add(db_key)
    print(token)
    user = {}
    for i in range(1, 4):
        user[i] = User(
            user_name="User{}".format(i),
            password="password{}".format(i),
        )
        db.session.add(user[i])
        playlist = {}
        for j in range(1, 4):
            playlist[j] = Playlist(
                name="Playlist{}".format(j),
                created_at = datetime.now(),
                user = user[i]
            )
            db.session.add(playlist[j])

        track = {}
        for j in range(1, 4):
            track[j] = Track(
                name="Track{}".format(j),
                artist ="Artist{}".format(j),
                duration = 100*j,
                user = user[i]
            )
            db.session.add(track[j])
        
        for j in range(1, 4):
            playlist_track = {}
            for k in range(1, 4):
                playlist_track[j] = PlaylistTrack(
                    track_number= j + k,
                    playlist =playlist[j],
                    track = track[j],
                )
                db.session.add(playlist_track[j])

    key = {}
    for i in range(1, 4):        
        key[i] = AuthenticateKey(
            key=AuthenticateKey.key_hash("User{}".format(i)),
            admin = False,
            user=user[i],
        )
        db.session.add(key[i])
    db.session.commit()