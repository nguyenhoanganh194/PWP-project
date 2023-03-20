from flask import Flask, request, jsonify
from sqlalchemy import MetaData

import models
from models import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///playlistmgt.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create database
with app.app_context():
    """
    Initializes a new database.
    """
    db.init_app(app)
    db.create_all()
    meta = MetaData(bind=db.engine)
    meta.reflect()
    # Get a list of table names
    table_names = meta.tables.keys()
    print(table_names)


# Route to get all playlists
@app.route('/playlists', methods=['GET'])
def get_playlists():
    playlists = models.Playlist.query.all()
    result = []
    for playlist in playlists:
        result.append({
            "id": playlist.id,
            "name": playlist.name,
            "user_id": playlist.user_id,
        })
        return jsonify(result), 200


# Route to create playlist
@app.route('/playlist', methods=['POST'])
def create_playlist():
    if not request.json:
        return jsonify({"message": "Request content type must be JSON"}), 415
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({"message": "Request content type must be JSON"}), 415
    if not all(key in request.json for key in ['name', 'user_id']):
        return jsonify({"message": "Incomplete request - missing fields"}), 400

    name = request.json['name']
    user_id = request.json['user_id']

    if not name or not user_id:
        return jsonify({"message": "Incomplete request - missing fields"}), 400

    if models.Playlist.query.filter_by(name=name).first():
        return jsonify({"message": "Playlist already exists"}), 409

    playlist = models.Playlist(name=name, user_id=user_id)
    db.session.add(playlist)
    db.session.commit()

    return jsonify({"message": "Playlist created successfully"}), 201


# Get a playlist by ID
@app.route('/playlist/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    playlist = models.Playlist.query.filter_by(id=playlist_id).first()
    if not playlist:
        return jsonify({"message": "Playlist not found"}), 404

    playlist_data = {
        "id": playlist.id,
        "name": playlist.name,
        "user_id": playlist.user_id,
        "tracks": []
    }

    for playlist_track in playlist.playlist_tracks:
        track = playlist_track.track
        playlist_data['tracks'].append({
            "id": track.id,
            "name": track.name,
            "artist": track.artist,
            "duration": track.duration,
            "user_id": playlist_track.user_id
        })

    return jsonify(playlist_data), 200


# Update a playlist
@app.route('/playlists/<int:playlist_id>', methods=['PUT'])
def update_playlist(playlist_id):
    if request.content_type != 'application/json':
        return jsonify({'message': 'Request content type must be JSON'}), 415

    try:
        data = request.get_json()
        if not data.get('name') or not data.get('user_id'):
            return jsonify({'message': 'Incomplete request - missing fields'}), 400

        playlist = models.Playlist.query.filter_by(id=playlist_id).first()
        if playlist is None:
            return jsonify({'message': 'Playlist not found'}), 404

        existing_playlist = models.Playlist.query.filter_by(name=data['name'], user_id=data['user_id']).first()
        if existing_playlist and existing_playlist.id != playlist_id:
            return jsonify({'message': 'Playlist already exists'}), 409

        playlist.name = data['name']
        playlist.user_id = data['user_id']
        db.session.commit()

        return jsonify({'message': 'Playlist updated successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Delete a playlist
@app.route('/playlists/<int:playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    try:
        playlist = models.Playlist.query.filter_by(id=playlist_id).first()
        if not playlist:
            return jsonify({'message': 'Playlist not found'}), 404

        db.session.delete(playlist)
        db.session.commit()

        return jsonify({'message': 'Playlist deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
