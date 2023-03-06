from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask.cli import with_appcontext
import models
from models import db
from resource.user import UsersResource
import random


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
api = Api(app)
api.add_resource(UsersResource, "/users/")

with app.app_context():
    """
    Initializes a new database.
    """
    db.init_app(app)
    db.create_all()
    meta = MetaData(bind=db.engine)
    meta.reflect()
    # Get a list of table names
    table_names = meta.tables.keys()
    print(table_names)

 #Test
@app.route("/user/add/",methods=["POST"])
def add_user():
    try:
        user = models.User(
            id = 12,
            user_name = "12",
            password = "12"
        )
        models.db.session.add(user)
        models.db.session.commit()
        return "Successful",201
    except:
        return "User already exists",409

    
@app.route("/playlist/<user_id>/add/",methods=["POST"])
def add_playlist(user_id):
    user = models.db.session.query(models.User).filter_by(id = user_id).scalar()
    
    if user is not None:
        playlist = models.Playlist(
            id = 12,
            name = "Playlist",
            description = "Playlist",
            of_user = user.id
        )
        models.db.session.add(playlist)
        models.db.session.commit()
        return "",201
    else:
        return "User not found",404

@app.route("/song/<user_id>/add/",methods=["POST"])
def add_song(user_id):
    user = models.db.session.query(models.User).filter_by(id = user_id).scalar()
    
    if user is not None:
        song = models.Song(
            id = 12,
            name = "Song",
            directory = "directory",
            genre = "genre",
            of_user = user.id
        )
        models.db.session.add(song)
        models.db.session.commit()
        return "",201
    else:
        return "User not found",404



@app.route("/add_to_playlist/<user_id>/<playlist_id>/<song_id>/add/",methods=["POST"])
def add_song_to_playlist(user_id,playlist_id,song_id):
    user = models.db.session.query(models.User).filter_by(id = user_id).scalar()
    #check if user, playlist ,song exist try except 
    playlist = models.db.session.query(models.Playlist).filter_by(id = user.id).scalar()
    song = models.db.session.query(models.Playlist).filter_by(id = user.id).scalar()
    if song is not None: 
        relationship = models.In_Playlist(
            playlist_id = playlist.id,
            song_id = song.id,
            order = 1,
        )
        models.db.session.add(relationship)
        models.db.session.commit()
        return "",201
    else:
        return "Playlist not found",404

   