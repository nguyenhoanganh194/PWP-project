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

class TestUserResource(object):
    RESOURCE_URL = "/api/user/"
    invalid_data = None #TODO: define invalid user. can use a list
    valid_data = None #TODO: define valid user. can use a list
    def test_get_collection(self, client):
        with client.app_context():
            populate_test_db(db)
            resp = client.get(self.RESOURCE_URL)
            assert resp.status_code == 200
            body = json.loads(resp.data)
            #TODO: check if list user show correctly
            #TODO: check if hypermedia show correctly
        pass

    def test_post_collection(self, client):
        with client.app_context():
            resp = client.post(self.RESOURCE_URL, data=json.dumps(self.valid_data))
        #TODO: check if that user is in database
        #TODO: check if location show correctly
        pass

    def test_get_item(self, client):
        #TODO: do same thing base on function tittle + hypermedia
        pass

    def test_put_item(self, client):
        #TODO: do same thing base on function tittle + hypermedia
        pass

    def test_delete_item(self, client):
        #TODO: do same thing base on function tittle + hypermedia
        pass

#TODO: do same thing for 3 other resource.