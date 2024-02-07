import json
from unittest.mock import patch, MagicMock
from playlistmanager import app, db
from playlistmanager.models import PlaylistTrack, Playlist, Track, User
from playlistmanager.constants import PLAYLIST_TRACK_PROFILE, MASON
from flask_testing import TestCase


class TestPlaylistTrackAPI(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()
        self.client = self.app.test_client()
        self.user = User(username='test_user', password='test_password')
        self.playlist = Playlist(title='test_playlist', user=self.user)
        self.track = Track(title='test_track', artist='test_artist', user=self.user)
        db.session.add_all([self.user, self.playlist, self.track])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_playlist_tracks(self):
        playlist_track = PlaylistTrack(track_number=1, playlist_id=self.playlist.id, track_id=self.track.id)
        self.playlist.playlist_tracks.append(playlist_track)
        db.session.add(playlist_track)
        db.session.commit()
        response = self.client.get(f'/api/users/{self.user.id}/playlists/{self.playlist.id}/tracks', headers={'Accept': MASON})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, MASON)
        data = json.loads(response.data.decode())
        self.assertEqual(len(data['items']), 1)
        item = data['items'][0]
        self.assertEqual(item['track_id'], self.track.id)
        self.assertEqual(item['playlist_id'], self.playlist.id)
        self.assertEqual(item['track_number'], 1)

    def test_add_playlist_track(self):
        playlist_track = {'track_number': 1, 'playlist_id': self.playlist.id, 'track_id': self.track.id}
        response = self.client.post(f'/api/users/{self.user.id}/playlists/{self.playlist.id}/tracks',
                                    headers={'Content-Type': 'application/json'}, data=json.dumps(playlist_track))
        self.assertEqual(response.status_code, 201)
        self.assertTrue('/api/users/' in response.headers['Location'])
        self.assertTrue('/playlists/' in response.headers['Location'])
        self.assertTrue('/tracks/' in response.headers['Location'])
        location_url = response.headers['Location']
        playlist_track_id = int(location_url.split('/')[-1])
        playlist_track = PlaylistTrack.query.get(playlist_track_id)
        self.assertIsNotNone(playlist_track)
        self.assertEqual(playlist_track.track_number, 1)
        self.assertEqual(playlist_track.playlist_id, self.playlist.id)
        self.assertEqual(playlist_track.track_id, self.track.id)