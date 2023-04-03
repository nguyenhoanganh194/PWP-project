import pytest
import json
from playlistmanager import create_app, db
from playlistmanager.models import User,Playlist,PlaylistTrack,Track, AuthenticateKey
from .conftest import populate_test_db

class TestUserResource(object):
    RESOURCE_URL = "/api/user/"
    invalid_data = None #TODO: define invalid user. can use a list
    valid_data = None #TODO: define valid user. can use a list
    @pytest.mark.usefixtures("client")
    def test_get_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.get(self.RESOURCE_URL)
            assert resp.status_code == 200
            body = json.loads(resp.data)
            check_namespace(app,body)
            assert len(body["items"]) == 3 
            for item in body["items"]:
                check_control_get_method(app,"self",item,200)
        
            check_control_post_method(app,"plm:add-user", body)

    def test_post_collection(self, client):
        with client.app_context():
            resp = client.post(self.RESOURCE_URL, data=json.dumps(self.valid_data))
        #TODO: check if that user is in database
        #TODO: check if location show correctly
        pass

    def test_get_item(self, client):
        #TODO: do same thing base on function tittle + hypermedia
        pass

    def test_put_item(self, client):
        #TODO: do same thing base on function tittle + hypermedia
        pass

    def test_delete_item(self, client):
        #TODO: do same thing base on function tittle + hypermedia
        pass

#TODO: do same thing for 3 other resource.

def check_namespace(client, body):
    """
    Checks that the "gss" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """
    ns_href = body["@namespaces"]["plm"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 302


def check_control_get_method(client, ctrl, obj, code=200):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """
    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == code

def check_control_post_method(client, ctrl, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid object against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    print(schema)
    # body = _get_json_object(model, number)
    # validate(body, schema)
    # resp = client.post(href, json=body)
    # assert resp.status_code == 201



def check_control_delete_method(client,ctrl , obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the control's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204