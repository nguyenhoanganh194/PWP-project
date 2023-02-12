from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask.cli import with_appcontext
db = SQLAlchemy()


class User(db.Model):
   
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False)
    
    playlists =  db.relationship("Playlist", cascade="all, delete-orphan",back_populates="of_user")
    #TODO: Define schema here later


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.String(64), nullable=False, default="descending")

    songs = db.relationship("Song", cascade="all, delete-orphan", back_populates="in_playlist")
    of_user = db.relationship("User", back_populates="playlists")
    #TODO: Define schema here later


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    directory = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(19), nullable=False)
    in_playlist = db.relationship("Playlist", back_populates="songs")
    #TODO: Define schema here later


