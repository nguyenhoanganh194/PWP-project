import unittest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from playlistmanager import db
from playlistmanager.models import Track
from playlistmanager.track import TrackCollection, TrackItem
from jsonschema import ValidationError


class TestTrackAPI(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.init_app(app)
        with app.app_context():
            db.create_all()
            user = User(username="test_user", password="password")
            db.session.add(user)
            db.session.commit()
            self.user = user

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_track_collection(self):
        with app.app_context():
            response = TrackCollection().get(self.user)
            self.assertEqual(response.status_code, 200)

    def test_post_track_collection(self):
        with app.app_context():
            data = {"name": "test_track", "artist": "test_artist", "duration": 300}
            response = TrackCollection().post(self.user, data=data)
            self.assertEqual(response.status_code, 201)

    def test_post_track_collection_invalid_json(self):
        with app.app_context():
            data = "not a JSON"
            response = TrackCollection().post(self.user, data=data)
            self.assertEqual(response.status_code, 415)

    def test_post_track_collection_invalid_data(self):
        with app.app_context():
            data = {"invalid_field": "test_track"}
            response = TrackCollection().post(self.user, data=data)
            self.assertEqual(response.status_code, 400)

    def test_get_track_item(self):
        with app.app_context():
            track = Track(name="test_track", artist="test_artist", duration=300, user=self.user)
            db.session.add(track)
            db.session.commit()
            response = TrackItem().get(self.user, track)
            self.assertEqual(response.status_code, 200)

    def test_get_track_item_not_owned(self):
        with app.app_context():
            user2 = User(name="test_user2")
            db.session.add(user2)
            db.session.commit()
            track = Track(name="test_track", artist="test_artist", duration=300, user=user2)
            db.session.add(track)
            db.session.commit()
            response = TrackItem().get(self.user, track)
            self.assertEqual(response.status_code, 409)

    def test_put_track_item(self):
        with app.app_context():
            track = Track(name="test_track", artist="test_artist", duration=300, user=self.user)
            db.session.add(track)
            db.session.commit()
            data = {"name": "test_track_updated"}
            response = TrackItem().put(self.user, track, data=data)
            self.assertEqual(response.status_code, 204)
            updated_track = Track.query.filter_by(id=track.id).first()
            self.assertEqual(updated_track.name, data["name"])

    def test_put_track_item_invalid_json(self):
        with app.app_context():
            track = Track(name="test_track", artist="test_artist", duration=300, user=self.user)
            db.session.add(track)
            db.session.commit()
            data = "not a JSON"
            response = TrackItem().put(self.user, track, data=data)
            self.assertEqual(response.status_code, 415)