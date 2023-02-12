from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask.cli import with_appcontext
import models
from models import db
import random


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


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
    print("Call")
    
    print("Call")
    user = models.User(
        id = random.random(),
        name = random.random(),
        password = random.random()
    )
    print("Call")
    models.db.session.add(user)
    models.db.session.commit()
    return "Successful",201


    
@app.route("/playlist/<user_id>/add/",methods=["POST"])
def add_playlist(user_id):
    user = models.db.session.query(models.User).filter_by(id = user_id).scalar()
    try:
        if user is not None:
            playlist = models.Playlist(
                id = random.random(),
                name = random.random(),
                description = random.random(),
                of_user = user
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