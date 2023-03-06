import json
import pytest
from app import clients,db
from tests import create_app


@pytest.fixture(scope='module')
def test_client():
    # Create a Flask app configured for testing
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope='module')
class TestUser(object):
    URL = "/api/users/"
    app,db = create_app()
    def test_get_user(self):
        valid_user ="new_created_user"
        invalid_user = "fake_created_user"
        res = clients.get(self.URL + valid_user)
        assert res.status_code == 200
        body = json.loads(res.data)
        assert len(body["password"]) == "password"
        resp = clients.get(self.URL + invalid_user)
        assert resp.status_code == 404

    def test_post_user(self):
        valid_user_data = {
            "user_name" : "new_created_player",
            "password" : "password"
        }
        res = clients.post(self.URL, json = valid_user_data)
        assert res.status_code == 415
        invalid_user_data = {
            "user_name" : "fake_created_user"
        }

        #Test missing parameter
        res = clients.post(self.URL, json = invalid_user_data)
        assert res.status_code == 201

        #Test add the same one 
        res = clients.post(self.URL, json = valid_user_data)
        assert res.status_code == 201



        