import pytest
from playlistmanager import create_app, db
from playlistmanager.models import User,Playlist,PlaylistTrack,Track, AuthenticateKey
from .conftest import populate_test_db

@pytest.mark.usefixtures("client")
def test_create_instances(client):
    with client.app_context():
        populate_test_db(db)
        assert User.query.count() == 3
        assert AuthenticateKey.query.count() == 4
        assert Playlist.query.count() == 9
        assert Track.query.count() == 9
        assert PlaylistTrack.query.count() == 27

@pytest.mark.usefixtures("client")
def test_delete_user(client):
    with client.app_context():
        populate_test_db(db)
        user = User.query.filter_by(user_name = "User1").first()
        db.session.delete(user)
        assert User.query.filter_by(user_name = "User1").first() is None
        assert AuthenticateKey.query.count() == 3

        playlist = Playlist.query.filter_by(user = user).first()
        track = Track.query.filter_by(user = user).first()
        assert playlist is None
        assert track is None

@pytest.mark.usefixtures("client")
def test_delete_track(client):
    with client.app_context():
        populate_test_db(db)
        user = User.query.filter_by(user_name = "User1").first()
        track = Track.query.filter_by(user = user).first()
        db.session.delete(track)
        playlist_track = PlaylistTrack.query.filter_by(track = track).first()

        assert Track.query.filter_by(id = track.id).first() is None
        assert playlist_track is None


@pytest.mark.usefixtures("client")
def test_delete_playlist(client):
    with client.app_context():
        populate_test_db(db)
        user = User.query.filter_by(user_name = "User1").first()
        playlist = Playlist.query.filter_by(user = user).first()
        db.session.delete(playlist)
        playlist_track = PlaylistTrack.query.filter_by(playlist = playlist).first()

        assert Playlist.query.filter_by(id = playlist.id).first() is None
        assert playlist_track is None

@pytest.mark.usefixtures("client")
def test_delete_playlist_track(client):
    with client.app_context():
        populate_test_db(db)
        user = User.query.filter_by(user_name = "User1").first()
        playlist = Playlist.query.filter_by(user = user).first()
        playlist_track = PlaylistTrack.query.filter_by(playlist = playlist).first()
        db.session.delete(playlist_track)
        assert PlaylistTrack.query.filter_by(id = playlist_track.id).first() is None

@pytest.mark.usefixtures("client")
def test_find_authenticate_key(client):
    with client.app_context():
        populate_test_db(db)
        user = User.query.filter_by(user_name = "User1").first()
        key = "User1"
        auth_key = AuthenticateKey.query.filter_by(key = AuthenticateKey.key_hash(key)).first()
        assert auth_key is not None
        assert auth_key.user == user
