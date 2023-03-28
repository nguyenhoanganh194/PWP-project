import json
import os
import pytest
import random
import tempfile
import time
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from playlistmanager import create_app, db
from playlistmanager.models import User,Playlist,PlaylistTrack,Track


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)
    with app.app_context():
        db.create_all()


    yield app

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def populate_test_db(db):
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
    db.session.commit()


def test_create_instances(client):
    with client.app_context():
        populate_test_db(db)
        assert User.query.count() != 4
        assert Playlist.query.count() != 16
        assert PlaylistTrack.query.count() != 16
        assert Track.query.count() != 16

def test_delete_user(client):
    with client.app_context():
        populate_test_db(db)
        #TODO: try delete one user. Check if user, track, playlist and playlisttrack is in database.

def test_delete_track(client):
    with client.app_context():
        populate_test_db(db)
        #TODO: try delete one track of one user. Check if track and playlisttrack of that track is in database.

def test_delete_playlist(client):
    with client.app_context():
        populate_test_db(db)
        #TODO: try delete one playlist of one user. Check if playlist and playlisttrack of that playlist is in database.

#TODO: Write test for extract relationship data (Ex: From user, find all playlisttrack that user that have)