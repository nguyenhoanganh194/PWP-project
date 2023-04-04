# PWP-project
 The PWP project oulu course
 

# Preface

The GameScoreService API is developed under Python 3.9.x and it's recommended to have at least Python 3.3 to have the necessary tools included. The API uses SQLite 3 database engine and Flask framework with SQLAlchemy toolkit.

The instructions shown in this file apply on Linux based environments.

# Set up instructions:
Set up env (window shell)
 ```console
 venv/Scripts/activate
 pip install -r requirements.txt
 $env:FLASK_APP = "playlistmanager"
 ```
 

# Preparations
Set up virtual environment (window shell)
 ```console
 py -3 -m venv venv
 venv/Scripts/activate
 $env:FLASK_APP = "playlistmanager"
 ```

# Installation
Exact requirements are listed in the requirements.txt file, which can be given to the pip command:  
```pip install -r requirements.txt```

# Running

 If no database created yet
 ```console
 flask init-db
 ```
 If create some fake data
 ```console
 flask populate-db
 ```
 
 Run the project
 ```console
 flask run
 ```
# Enrty Point

The API is available at /api/ URI on the system you run it. By default it opens in the port 5000.
```http://localhost:5000/api/```

You can access swagger UI.
```http://localhost:5000/```

# Testing

Execute the following lines when virtual environment is active:  
```
pip install pytest
pip install pytest-cov
```

To run all the test. Use the following command
```
python -m py.test
```
With more detailed coverage reports.
```
python -m py.test --cov-report term-missing --cov=playlistmanager
```