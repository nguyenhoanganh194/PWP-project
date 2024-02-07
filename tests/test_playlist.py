import unittest
from unittest.mock import MagicMock, patch
from playlistmanager.models import *
from playlistmanager.playlist import *


# test_models.py
class PlaylistTests(unittest.TestCase):
    def setUp(self):
        self.playlist = Playlist()

    def test_serialize(self):
        self.playlist.id = 1
        self.playlist.name = 'Test Playlist'
        self.playlist.created_at = '2023-04-10 12:00:00'
        expected = {
            "id": 1,
            "name": "Test Playlist",
            "created_at": "2023-04-10T12:00:00"
        }
        self.assertEqual(self.playlist.serialize(), expected)

    def test_deserialize(self):
        doc = {
            "name": "Test Playlist",
            "created_at": "2023-04-10T12:00:00"
        }
        self.playlist.deserialize(doc)
        self.assertEqual(self.playlist.name, "Test Playlist")
        self.assertEqual(self.playlist.created_at.isoformat(), "2023-04-10T12:00:00")

    def test_get_schema(self):
        schema = Playlist.get_schema()
        self.assertEqual(schema["type"], "object")
        self.assertEqual(schema["required"], ["name", "created_at"])
        self.assertEqual(schema["properties"]["name"]["description"], "Playlist name")
        self.assertEqual(schema["properties"]["name"]["type"], "string")
        self.assertEqual(schema["properties"]["created_at"]["description"], "Date time created")
        self.assertEqual(schema["properties"]["created_at"]["type"], "string")
        self.assertEqual(schema["properties"]["created_at"]["format"], "date-time")


# test_api.py
class PlaylistCollectionTests(unittest.TestCase):
    def setUp(self):
        self.user = MagicMock()
        self.playlist_collection = PlaylistCollection()

    @patch("Playlist.request")
    @patch("Playlist.validate")
    def test_post(self, mock_validate, mock_request):
        mock_request.json = {"name": "Test Playlist", "created_at": "2023-04-10T12:00:00"}
        mock_validate.return_value = True
        self.playlist_collection.post(self.user)
        self.user.playlists.append.assert_called_once()

    @patch("Playlist.request")
    def test_post_invalid_json(self, mock_request):
        mock_request.json = None
        response = self.playlist_collection.post(self.user)
        self.assertEqual(response.status_code, 415)

    @patch("Playlist.request")
    @patch("Playlist.validate")
    def test_post_invalid_document(self, mock_validate, mock_request):
        mock_request.json = {"name": "Test Playlist"}
        mock_validate.side_effect = Exception("Invalid document")
        response = self.playlist_collection.post(self.user)
        self.assertEqual(response.status_code, 400)

    def test_get(self):
        self.user.playlists = [MagicMock(), MagicMock()]
        response = self.playlist_collection.get(self.user)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["items"]), 2)


class PlaylistItemTests(unittest.TestCase):
    def setUp(self):
        self.user = MagicMock()
        self.playlist = MagicMock()
        self.playlist_item = PlaylistItem()

    def test_get(self):
        self.playlist.user = self.user
        response = self.playlist_item.get(self.user, self.playlist)
        self.assertEqual(response.status_code, 200)

    def test_get_invalid_user(self):
        self.playlist.user = MagicMock()
        response = self.playlist_item.get(self.user, self.playlist)
        self.assertEqual(response.status_code, 409)

    @patch("Playlist.request")
    def test_put(self, mock_request):
        self.playlist.user = self.user
        mock_request.json = {"name": "New Playlist Name"}
