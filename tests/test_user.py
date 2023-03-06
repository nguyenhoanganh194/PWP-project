import json
import os
import pytest
import tempfile
from sqlalchemy import MetaData
from tests import create_app
from flask.cli import with_appcontext


@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app,db = create_app(config)

    with app.app_context():
        db.init_app(app)
        db.create_all()
        meta = MetaData(bind=db.engine)
        meta.reflect()
        # Get a list of table names
        table_names = meta.tables.keys()
        print(table_names)

    yield app

    os.close(db_fd)
    os.unlink(db_fname)

def test_client():
    URL = "/api/users/"
    assert client() is None





class TestPlayerCollection(object):
    URL = "/api/users/"
    def test_get_user(self):
        valid_user ="new_created_user"
        invalid_user = "fake_created_user"
        res = client.get(self.URL + valid_user)
        assert res.status_code == 200
        body = json.loads(res.data)
        assert len(body["password"]) == "password"
        resp = client.get(self.URL + invalid_user)
        assert resp.status_code == 404

    def test_post_user(self):
        valid_user_data = {
            "user_name" : "new_created_player",
            "password" : "password"
        }
        res = client.post(self.URL, json = valid_user_data)
        assert res.status_code == 415
        invalid_user_data = {
            "user_name" : "fake_created_user"
        }

        #Test missing parameter
        res = client.post(self.URL, json = invalid_user_data)
        assert res.status_code == 201

        #Test add the same one 
        res = client.post(self.URL, json = valid_user_data)
        assert res.status_code == 201



        