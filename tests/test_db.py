import pytest
from playlistmanager import create_app, db
from playlistmanager.models import User,Playlist,PlaylistTrack,Track, AuthenticateKey
from .conftest import populate_test_db

@pytest.mark.usefixtures("client")
def test_create_instances(client):
    with client.app_context():
        populate_test_db(db)
        assert User.query.count() != 4
        assert AuthenticateKey.query.count() != 5
        assert Playlist.query.count() != 16
        assert PlaylistTrack.query.count() != 16
        assert Track.query.count() != 16

@pytest.mark.usefixtures("client")
def test_delete_user(client):
    with client.app_context():
        populate_test_db(db)
        #TODO: try delete one user. Check if user, track, playlist and playlisttrack is in database.

@pytest.mark.usefixtures("client")
def test_delete_track(client):
    with client.app_context():
        populate_test_db(db)
        #TODO: try delete one track of one user. Check if track and playlisttrack of that track is in database.

@pytest.mark.usefixtures("client")
def test_delete_playlist(client):
    with client.app_context():
        populate_test_db(db)
        #TODO: try delete one playlist of one user. Check if playlist and playlisttrack of that playlist is in database.

#TODO: Write test for extract relationship data (Ex: From user, find all playlisttrack that user that have)