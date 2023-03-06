from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    user_name  = db.Column(db.String(64), nullable=False, unique=True)
    password  = db.Column(db.String(64), nullable=False)

    playlists = db.relationship("Playlist", cascade="all, delete-orphan", back_populates="user")
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

class Playlist(db.Model):
    __tablename__ = "Playlist"
    id = db.Column(db.Integer, primary_key=True)
    tittle = db.Column(db.String(64), nullable=False)
    date_created = db.Column(db.String(64), nullable=False, default="descending")

    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    songs = db.relationship("Song", secondary="In_Playlist")
    
    user = db.relationship("User", back_populates="playlists")
    #TODO: Define schema here later


class Song(db.Model):
    __tablename__ = "Song"
    id = db.Column(db.Integer, primary_key=True)
    tittle = db.Column(db.String(64), nullable=False)
    directory = db.Column(db.String(256), nullable=False)
    genre = db.Column(db.String(19), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    #TODO: Define schema here later


class Playlist_track(db.Model):
    __tablename__ = "Playlist_track"

    playlist_id = db.Column(sa.ForeignKey("Playlist.id"), primary_key=True)
    song_id = db.Column(sa.ForeignKey("Song.id"), primary_key=True)
    track_number = db.Column(sa.Integer)