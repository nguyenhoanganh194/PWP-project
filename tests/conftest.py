import pytest
import os
import time
from datetime import datetime
import tempfile
from playlistmanager.models import User,Playlist,PlaylistTrack,Track, AuthenticateKey
from playlistmanager import create_app, db
import secrets

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
    db_key = AuthenticateKey(
        key= AuthenticateKey.key_hash("admin_token"),
        admin=True
    )
    db.session.add(db_key)
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