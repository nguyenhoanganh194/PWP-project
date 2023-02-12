from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
import models
import random


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
 #Test
@app.route("/user/add/",methods=["POST"])
def add_user():
    try:
        item = models.User(
            id = random.random(),
            name = random.random(),
            password = random.random()
        )
        models.db.session.add(item)
        models.db.session.commit()
        return "Successful",201
    except:
        return "User already exists",409

    
@app.route("/playlist/<user_id>/add/",methods=["POST"])
def add_playlist(user_id):
    user = models.db.session.query(models.User).filter_by(id = user_id).scalar()
    try:
        if user is not None:
            playlist = models.Playlist(
                id = random.random(),
                name = random.random(),
                description = random.random()
            )
            models.db.session.add(playlist)
            models.db.session.commit()
            return "",201
        else:
            return "User not found",404
    except:
        return "Unexpected error", 500 

@app.route("/playlist/<user_id>/<playlist_id>/add/",methods=["POST"])
def add_song(user_id):
    user = models.db.session.query(models.User).filter_by(id = user_id).scalar()
    playlist = models.db.session.query(models.Playlist).filter_by(handle = user).scalar()
    try:
        if playlist is not None: 
            playlist = models.Song(
                id = random.random(),
                name = random.random(),
                directory = "directory",
                genre = "genre",
                in_playlist = playlist,
            )
            models.db.session.add(playlist)
            models.db.session.commit()
            return "",201
        else:
            return "Playlist not found",404
    except:
        return "Unexpected error", 500 