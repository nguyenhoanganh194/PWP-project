import unittest
from app import app, db
from models import Playlist, PlaylistTrack, User, Track


# Note that this code assumes that there are already defined the db from models file.

class PlaylistTestCase(unittest.TestCase):
    def setUp(self):
        # sets up a temporary SQLite database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.create_all()

        # Create test users
        self.user1 = User(name='Alice', password='password')
        self.user2 = User(name='Bob', password='password')
        db.session.add_all([self.user1, self.user2])
        db.session.commit()
        # Create test tracks
        self.track1 = Track(name='Test track 1', artist='Test artist 1', duration=180)
        self.track2 = Track(name='Test track 2', artist='Test artist 2', duration=240)
        db.session.add_all([self.track1, self.track2])
        db.session.commit()
        # Create test playlist
        self.playlist = Playlist(name='Dumb Test Playlist', user=self.user1)
        db.session.add(self.playlist)
        db.session.commit()

        # Create test playlist tracks
        self.playlist_track1 = PlaylistTrack(playlist=self.playlist, track=self.track1, user=self.user1)
        self.playlist_track2 = PlaylistTrack(playlist=self.playlist, track=self.track2, user=self.user1)
        db.session.add_all([self.playlist_track1, self.playlist_track2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_playlist(self):
        user = User(name='John Doe', password='paassword')
        playlist = Playlist(name='My Playlist', user=user)
        track = Track(name='Track 1', artist='Artist 1', duration=180)
        playlist_track = PlaylistTrack(playlist=playlist, track=track, user=user)
        db.session.add_all([user, playlist, track, playlist_track])
        db.session.commit()

        response = self.client.get(f'/playlist/{playlist.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data['id'], playlist.id)
        self.assertEqual(data['name'], playlist.name)
        self.assertEqual(data['user_id'], user.id)
        self.assertEqual(len(data['tracks']), 1)
        self.assertEqual(data['tracks'][0]['id'], track.id)
        self.assertEqual(data['tracks'][0]['name'], track.name)
        self.assertEqual(data['tracks'][0]['artist'], track.artist)
        self.assertEqual(data['tracks'][0]['duration'], track.duration)
        self.assertEqual(data['tracks'][0]['added_by'], user.id)

    def test_get_playlist_not_found(self):
        response = self.client.get('/playlist/999')
        self.assertEqual(response.status_code, 404)
        data = response.json
        self.assertEqual(data['error'], 'Playlist not found')

    # Sends a POST request to the create playlist with the user ID and playlist data
    def test_create_playlist(self):
        user = User(name='John')
        db.session.add(user)
        db.session.commit()

        data = {
            'name': 'My Playlist',
            'description': 'A playlist of my so favorite tracks.',
            'user_id': user.id
        }
        response = self.app.post('/playlists', json=data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Playlist.query.count(), 1)

        playlist = Playlist.query.first()
        self.assertEqual(playlist.name, data['name'])
        self.assertEqual(playlist.description, data['description'])
        self.assertEqual(playlist.user_id, data['user_id'])

    def test_update_playlist(self):
        data = {'user_id': self.user2.id, 'track_ids': [self.track1.id]}
        response = self.client.put('/playlists/{}/'.format(self.playlist.id), json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['user']['id'], self.user2.id)
        self.assertEqual(len(response.json['tracks']), 1)
        self.assertEqual(response.json['tracks'][0]['id'], self.track1.id)
        self.assertIsNone(PlaylistTrack.query.filter_by(playlist_id=self.playlist.id, track_id=self.track2.id).first())
        self.assertIsNotNone(
            PlaylistTrack.query.filter_by(playlist_id=self.playlist.id, track_id=self.track1.id).first())

    def test_delete_playlist(self):
        user = User(username='testuser', password='password')
        playlist = Playlist(name='Test Playlist', user=user)
        with app.app_context():
            db.session.add(user)
            db.session.add(playlist)
            db.session.commit()
        response = self.app.delete(f'/playlists/{playlist.id}')
        with app.app_context():
            playlists = Playlist.query.all()
            self.assertEqual(len(playlists), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['success'], 'Playlist deleted successfully')

    def test_delete_nonexistent_playlist(self):
        response = self.app.delete('/playlists/123')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['error'], 'Playlist not found.')
