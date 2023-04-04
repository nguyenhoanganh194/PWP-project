import secrets
import pytest
import json
from playlistmanager import create_app, db
from playlistmanager.models import User,Playlist,PlaylistTrack,Track, AuthenticateKey
from .conftest import populate_test_db
from jsf import JSF

class TestUserResource(object):
    RESOURCE_URL = "/api/user/"
    valid_data = {'user_name': 'officiis ipsum, Lorem', 'password': 'culpa! repellendus accusantium'}
    invalid_data = {'user_name': 'officiis ipsum, Lorem'}
    @pytest.mark.usefixtures("client")
    def test_get_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.get(self.RESOURCE_URL)
            assert resp.status_code == 200
            body = json.loads(resp.data)
            check_namespace(app,body)
            for item in body["items"]:
                check_control_get_method(app,"self",item,200)

            check_control_post_method(app,"plm:add-user", body)

    def test_post_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.post(self.RESOURCE_URL,data=json.dumps(self.valid_data))
            assert resp.status_code == 415
            resp = app.post(self.RESOURCE_URL, json=self.valid_data)
            assert resp.status_code == 201
            resp = app.post(self.RESOURCE_URL, json=self.valid_data)
            assert resp.status_code == 409
            resp = app.post(self.RESOURCE_URL, json=self.invalid_data)
            assert resp.status_code == 400

    def test_get_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)

            resp = app.get(self.RESOURCE_URL + "User100/")
            assert resp.status_code == 404
            resp = app.get(self.RESOURCE_URL + "User1/")
            assert resp.status_code == 200
            
            body = json.loads(resp.data)
            check_namespace(app,body)
            check_control_get_method(app,"profile", body, 302)
            check_control_get_method(app,"collection", body)
            check_control_get_method(app,"self", body)
            check_control_get_method(app,"plm:tracks-of", body)
            check_control_get_method(app,"plm:playlists-of", body)
            check_control_put_method(app,"plm:edit-user", body,"User1")

            resp = app.get(self.RESOURCE_URL + "User2/")
            body = json.loads(resp.data)
            check_control_delete_method(app,"plm:delete", body,"User2")

            resp = app.get(self.RESOURCE_URL + "User3/")
            body = json.loads(resp.data)
            check_control_delete_method(app,"plm:delete", body,"User4", 403)


    def test_put_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            headers = {
                "authenticate_key": "User1"
            }
            resp = app.put(self.RESOURCE_URL + "User1/",headers = headers,data=json.dumps(self.valid_data))
            assert resp.status_code == 415
            resp = app.put(self.RESOURCE_URL + "User1/",headers = headers,json=self.valid_data)
            assert resp.status_code == 301
            resp = app.get(resp.headers.get("location"))
            assert resp.status_code == 200
            
            headers = {
                "authenticate_key": "User2"
            }
            self.valid_data["user_name"] = "User3"
            resp = app.put(self.RESOURCE_URL + "User2/",headers = headers,json=self.valid_data)
            assert resp.status_code == 409

            headers = {
                "authenticate_key": "Random"
            }
            resp = app.put(self.RESOURCE_URL + "User2/",headers = headers,json=self.valid_data)
            assert resp.status_code == 403

            headers = {
                "authenticate_key": "User3"
            }
            resp = app.put(self.RESOURCE_URL + "User3/",headers = headers,json=self.invalid_data)
            assert resp.status_code == 400

    def test_delete_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            headers = {
                "authenticate_key": "User1"
            }
            resp = app.delete(self.RESOURCE_URL + "User1/",headers = headers)
            assert resp.status_code == 204

            resp = app.delete(self.RESOURCE_URL + "User2/")
            assert resp.status_code == 403
           

#TODO: do same thing for 3 other resource.

def check_namespace(client, body):
    """
    Checks that the namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """
    ns_href = body["@namespaces"]["plm"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 302


def check_control_get_method(client, ctrl, obj, code = 200):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """
    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == code

def check_control_post_method(client, ctrl, obj,api_key = "", expect_code = 201):
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
    faker = JSF(schema)
    body = faker.generate()
    headers = {
        "Content-Type": "application/json; charset=utf-8;",
        "authenticate_key": api_key
    }
    resp = client.post(href, headers = headers,json=body)
    assert resp.status_code == expect_code

def check_control_put_method(client, ctrl, obj, api_key = "", expect_code = 301):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid object against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """
    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    faker = JSF(schema)
    body = faker.generate()
    headers = {
        "Content-Type": "application/json; charset=utf-8;",
        "authenticate_key": api_key
    }

    resp = client.put(href, headers = headers,json=body)
    assert resp.status_code == expect_code


def check_control_delete_method(client,ctrl, obj, api_key = "", expect_code = 204):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the control's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """
   
    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    headers = {
        "Content-Type": "application/json; charset=utf-8;",
        "authenticate_key": api_key
    }
    resp = client.delete(href,headers=headers)
    assert resp.status_code == expect_code
