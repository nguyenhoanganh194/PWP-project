import unittest
from playlistmanager import create_app, db
from playlistmanager.models import Playlist, Track, User, PlaylistTrack
import json


class TestPlaylistTrack(unittest.TestCase):

    def setUp(self):
        """
        Initializes the database and creates a test client.
        """
        self.app = create_app("testing")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            user = User(username="testuser", password="password")
            db.session.add(user)
            db.session.commit()
            playlist = Playlist(title="Test Playlist", user=user)
            db.session.add(playlist)
            db.session.commit()
            track = Track(title="Test Track", artist="Test Artist", album="Test Album", duration=200)
            db.session.add(track)
            db.session.commit()
            self.playlist_track = PlaylistTrack(track_number=1, playlist_id=playlist.id, track_id=track.id)
            db.session.add(self.playlist_track)
            db.session.commit()

    def tearDown(self):
        """
        Drops the database tables and removes the test client.
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_playlist_track_model(self):
        """
        Tests the PlaylistTrack model.
        """
        self.assertEqual(self.playlist_track.track_number, 1)
        self.assertEqual(self.playlist_track.playlist_id, 1)
        self.assertEqual(self.playlist_track.track_id, 1)

    def test_get_playlist_track_collection(self):
        """
        Tests the GET method for the PlaylistTrackCollection resource.
        """
        response = self.client.get("/api/users/testuser/playlists/1/playlisttracks")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertIn("items", data)

    def test_post_playlist_track_collection(self):
        """
        Tests the POST method for the PlaylistTrackCollection resource.
        """
        track_data = {
            "track_number": 2,
            "track_id": 1,
            "playlist_id": 1
        }
        response = self.client.post("/api/users/testuser/playlists/1/playlisttracks", json=track_data)
        self.assertEqual(response.status_code, 201)
        location = response.headers.get("Location")
        self.assertIsNotNone(location)

    def test_get_playlist_track_item(self):
        """
        Tests the GET method for the PlaylistTrackItem resource.
        """
        response = self.client.get("/api/users/testuser/playlists/1/playlisttracks/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data["track_number"], 1)

    def test_put_playlist_track_item(self):
        """
        Tests the PUT method for the PlaylistTrackItem resource.
        """
        track_data = {
            "track_number": 2,
            "track_id": 1,
            "playlist_id": 1
        }
        response = self.client.put("/api/users/testuser/playlists/1/playlisttracks/1", json=track_data)
        self.assertEqual(response.status_code, 204)

    def test_delete_playlist_track_item(self):
        """
        Tests the DELETE method for the PlaylistTrackItem resource.
        """
        response = self.client.delete("/api/users/testuser/playlists/1/playlisttracks/1")
        self.assertEqual(response.status_code, 204)
