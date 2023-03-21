from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
import click

db = SQLAlchemy()

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


class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    user_name  = db.Column(db.String(64), nullable=False, unique=True)
    password  = db.Column(db.String(64), nullable=False)

    playlists = db.relationship("Playlist", cascade="all, delete-orphan", back_populates="user")

    def serialize(self):
        return {
            "user_name": self.user_name, 
            "password": self.password,
            "playlists": self.playlists.serialize(),
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
    
    def serialize(self):
        pass
    
    def deserialize(self, doc):
        pass

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
