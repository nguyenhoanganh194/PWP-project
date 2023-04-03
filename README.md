# PWP-project
 The PWP project oulu course
 
 ## Set up instructions:
 Set up env (window shell)
 ```console
 venv/Scripts/activate
 pip install -r requirements.txt
 $env:FLASK_APP = "playlistmanager"
 ```
 
 If no database created yet
 ```console
 flask init-db
 ```
 If create some fake data
 ```console
 flask populate-db
 ```
 Run all test
 ```console
 python -m py.test
 python -m py.test --cov-report term-missing --cov=playlistmanager
 ```
 Run the project
 ```console
 flask run
 ```
## Project Database Instructions:

There are playlist management database models class named 'Playlist', 'PlaylistTrack', 'Track' and 'User'. 

The Playlist model represents a playlist, with a foreign key to the User model, which contains the user's personal information. 

The Track model represents a track, with fields for the name, artist, and duration of the track. The PlaylistTrack model represents the relationship between a playlist and a track, with foreign keys to the Playlist, Track, and User models, representing the playlist the track is in, the track itself, and the user who added the track to the playlist, respectively. 

The dependencies of the project are provided in the file requirements.txt. 

The main database engine used in the project is SQLite, we interact with the database using the Flask SQLAlchemy toolkit.

the user can populate the database using the flask shell or the existing tests in the app.py file, using the shell as the following example:


```console
>>> from models import db, User
>>> User_John = User(user_name='john97', password='john1997')
>>> db.session.add(User_John)
>>> db.session.commit()
```
 a test is also included in unittest.py
