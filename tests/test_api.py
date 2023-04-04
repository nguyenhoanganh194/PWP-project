import datetime
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
    headers = {
                "authenticate_key": "admin_token"
    }
    @pytest.mark.usefixtures("client")
    def test_entry_point(self,client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.get("/api/")
            assert resp.status_code == 200
            body = json.loads(resp.data)
            check_namespace(app,body)
            check_control_get_method(app,"plm:users-all", body)

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

            check_control_post_method(app,"plm:add-user", body,api_key=self.headers["authenticate_key"])

    def test_post_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.post(self.RESOURCE_URL,headers = self.headers,data=json.dumps(self.valid_data))
            assert resp.status_code == 415
            resp = app.post(self.RESOURCE_URL,headers = self.headers, json=self.invalid_data)
            assert resp.status_code == 400
            resp = app.post(self.RESOURCE_URL,headers = self.headers, json=self.valid_data)
            assert resp.status_code == 201


        
            headers = {
                "authenticate_key": "User2"
            }
            resp = app.post(self.RESOURCE_URL,headers = headers, json=self.valid_data)
            assert resp.status_code == 403

            resp = app.post(self.RESOURCE_URL,headers = self.headers, json=self.valid_data)
            assert resp.status_code == 409

            

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
           
class TestPlaylistResource(object):
    RESOURCE_URL = "/api/playlist/"
    valid_data = {'name': 'officiis ipsum, Lorem', 'created_at':  "1973-01-04T22:23:29+00:00" }
    invalid_data = {'name': 'officiis ipsum, Lorem'}
    @pytest.mark.usefixtures("client")
    def test_get_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.get(self.RESOURCE_URL + "User1/")
            assert resp.status_code == 200
            body = json.loads(resp.data)
            check_namespace(app,body)
            for item in body["items"]:
                check_control_get_method(app,"self",item,200)

            check_control_post_method(app,"plm:add-playlist", body)

    def test_post_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.post(self.RESOURCE_URL + "User1/",data=json.dumps(self.valid_data))
            assert resp.status_code == 415

            resp = app.post(self.RESOURCE_URL + "User1/", json=self.valid_data)
            assert resp.status_code == 201
            resp = app.get(resp.headers.get("location"))
            assert resp.status_code == 200

            resp = app.post(self.RESOURCE_URL + "User1/", json=self.invalid_data)
            assert resp.status_code == 400

    def test_get_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)

            resp = app.get(self.RESOURCE_URL + "User1/10/")
            assert resp.status_code == 404
            resp = app.get(self.RESOURCE_URL + "User1/1/")
            assert resp.status_code == 200
            
            body = json.loads(resp.data)
            check_namespace(app,body)
            check_control_get_method(app,"profile", body, 302)
            check_control_get_method(app,"collection", body)
            check_control_get_method(app,"self", body)

            check_control_put_method(app,"plm:edit-playlist", body)
            
            resp = app.get(self.RESOURCE_URL + "User1/2/")
            body = json.loads(resp.data)
            check_control_delete_method(app,"plm:delete", body)

            resp = app.get(self.RESOURCE_URL + "User3/3/")
            assert resp.status_code == 409


    def test_put_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)

            resp = app.put(self.RESOURCE_URL + "User1/1/",data=json.dumps(self.valid_data))
            assert resp.status_code == 415
            resp = app.put(self.RESOURCE_URL + "User1/1/",json=self.valid_data)
            assert resp.status_code == 301
            resp = app.get(resp.headers.get("location"))
            assert resp.status_code == 200
            
            resp = app.put(self.RESOURCE_URL + "User2/2/",json=self.valid_data)
            assert resp.status_code == 409
            
            self.valid_data["created_at"] = "Not date time"
            resp = app.put(self.RESOURCE_URL + "User1/2/",json=self.valid_data)
            assert resp.status_code == 400

            resp = app.put(self.RESOURCE_URL + "User1/2/",json=self.invalid_data)
            assert resp.status_code == 400



    def test_delete_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.delete(self.RESOURCE_URL + "User1/1/")
            assert resp.status_code == 204
            
            resp = app.delete(self.RESOURCE_URL + "User1/1/")
            assert resp.status_code == 404

            resp = app.delete(self.RESOURCE_URL + "User2/2/")
            assert resp.status_code == 409
           
class TestTrackResource(object):
    RESOURCE_URL = "/api/track/"
    valid_data = {'name': 'reiciendis Hic molestias, illum dolor dolor elit.', 'artist': 'culpa! exercitationem', 'duration': 5811.0}
    invalid_datas = [ 
        {'name': 'reiciendis Hic molestias, illum dolor dolor elit.', 'duration': 5811.0},
        {'name': 'reiciendis Hic molestias, illum dolor dolor elit.', 'artist': 'culpa! exercitationem'}
    ]
   
    @pytest.mark.usefixtures("client")
    def test_get_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.get(self.RESOURCE_URL + "User1/")
            assert resp.status_code == 200
            body = json.loads(resp.data)
            check_namespace(app,body)
            for item in body["items"]:
                check_control_get_method(app,"self",item,200)

            check_control_post_method(app,"plm:add-track", body)

    def test_post_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.post(self.RESOURCE_URL + "User1/",data=json.dumps(self.valid_data))
            assert resp.status_code == 415

            resp = app.post(self.RESOURCE_URL + "User1/", json=self.valid_data)
            assert resp.status_code == 201
            resp = app.get(resp.headers.get("location"))
            assert resp.status_code == 200

            for invalid_data in self.invalid_datas:
                resp = app.post(self.RESOURCE_URL + "User1/", json=invalid_data)
                assert resp.status_code == 400

    def test_get_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)

            resp = app.get(self.RESOURCE_URL + "User1/10/")
            assert resp.status_code == 404
            resp = app.get(self.RESOURCE_URL + "User1/1/")
            assert resp.status_code == 200
            
            body = json.loads(resp.data)
            check_namespace(app,body)
            check_control_get_method(app,"profile", body, 302)
            check_control_get_method(app,"collection", body)
            check_control_get_method(app,"self", body)

            check_control_put_method(app,"plm:edit-track", body)
            
            resp = app.get(self.RESOURCE_URL + "User1/2/")
            body = json.loads(resp.data)
            check_control_delete_method(app,"plm:delete", body)

            resp = app.get(self.RESOURCE_URL + "User3/3/")
            assert resp.status_code == 409


    def test_put_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)

            resp = app.put(self.RESOURCE_URL + "User1/1/",data=json.dumps(self.valid_data))
            assert resp.status_code == 415
            resp = app.put(self.RESOURCE_URL + "User1/1/",json=self.valid_data)
            assert resp.status_code == 301
            resp = app.get(resp.headers.get("location"))
            assert resp.status_code == 200

            resp = app.put(self.RESOURCE_URL + "User3/3/",json=self.valid_data)
            assert resp.status_code == 409

            resp = app.put(self.RESOURCE_URL + "User1/2/",json=self.invalid_datas[0])
            assert resp.status_code == 400



    def test_delete_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.delete(self.RESOURCE_URL + "User1/1/")
            assert resp.status_code == 204

            resp = app.delete(self.RESOURCE_URL + "User2/1")
            assert resp.status_code == 404

            resp = app.delete(self.RESOURCE_URL + "User3/3/")
            assert resp.status_code == 409

class TestPlaylistTrackResource(object):
    RESOURCE_URL = "/api/playlist_track/"
    valid_data = {'track_id': 1, 'playlist_id': 1, 'track_number': 2}
    invalid_datas = [ 
        {'track_id': 1, 'track_number': 2},
        {'track_id': 1, 'playlist_id': 1}
    ]
   
    @pytest.mark.usefixtures("client")
    def test_get_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.get(self.RESOURCE_URL + "User1/1/")
            assert resp.status_code == 200
            body = json.loads(resp.data)
            check_namespace(app,body)
            for item in body["items"]:
                check_control_get_method(app,"self",item,200)

            check_control_post_method(client=app,ctrl="plm:add-playlisttrack", obj=body, body= self.valid_data)

            resp = app.get(self.RESOURCE_URL + "User1/8/")
            assert resp.status_code == 409

    def test_post_collection(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.post(self.RESOURCE_URL + "User1/1/",data=json.dumps(self.valid_data))
            assert resp.status_code == 415

            resp = app.post(self.RESOURCE_URL + "User1/1/", json=self.valid_data)
            assert resp.status_code == 201
            resp = app.get(resp.headers.get("location"))
            assert resp.status_code == 200

            valid_data = {'track_id': 10, 'playlist_id': 1, 'track_number': 2}
            resp = app.post(self.RESOURCE_URL + "User1/1/", json=valid_data)
            assert resp.status_code == 409

            valid_data = {'track_id': 1, 'playlist_id': 1, 'track_number': 2}
            resp = app.post(self.RESOURCE_URL + "User1/8/", json=valid_data)
            assert resp.status_code == 409

            for invalid_data in self.invalid_datas:
                resp = app.post(self.RESOURCE_URL + "User1/1/", json=invalid_data)
                assert resp.status_code == 400

    def test_get_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)

            resp = app.get(self.RESOURCE_URL + "User1/1/100/")
            assert resp.status_code == 404
            resp = app.get(self.RESOURCE_URL + "User1/1/1/")
            assert resp.status_code == 200
            
            body = json.loads(resp.data)
            check_namespace(app,body)
            check_control_get_method(app,"profile", body, 302)
            check_control_get_method(app,"collection", body)
            check_control_get_method(app,"self", body)
            check_control_get_method(app,"track", body)

            check_control_put_method(app,"plm:edit-playlisttrack", obj=body,body= self.valid_data)
            
            resp = app.get(self.RESOURCE_URL + "User1/1/2/")
            body = json.loads(resp.data)
            check_control_delete_method(app,"plm:delete", body)

            resp = app.get(self.RESOURCE_URL + "User1/1/10/")
            assert resp.status_code == 409


    def test_put_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)

            resp = app.put(self.RESOURCE_URL + "User1/1/1/",data=json.dumps(self.valid_data))
            assert resp.status_code == 415
            resp = app.put(self.RESOURCE_URL + "User1/1/1/",json=self.valid_data)
            assert resp.status_code == 301
            resp = app.get(resp.headers.get("location"))
            assert resp.status_code == 200

            resp = app.put(self.RESOURCE_URL + "User1/1/1/",json=self.invalid_datas[0])
            assert resp.status_code == 400

            resp = app.put(self.RESOURCE_URL + "User1/4/3/",json=self.valid_data)
            assert resp.status_code == 409


    def test_delete_item(self, client):
        with client.app_context():
            app = client.test_client()
            populate_test_db(db)
            resp = app.delete(self.RESOURCE_URL + "User1/1/1/")
            assert resp.status_code == 204

            resp = app.delete(self.RESOURCE_URL + "User1/1/1/")
            assert resp.status_code == 404

            resp = app.delete(self.RESOURCE_URL + "User1/2/3/")
            assert resp.status_code == 409


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

def check_control_post_method(client, ctrl, obj ,api_key = "", body = None, expect_code = 201):
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
    headers = {
        "Content-Type": "application/json; charset=utf-8;",
        "authenticate_key": api_key
    }
    if body == None:
        faker = JSF(schema)
        body = faker.generate()
   
    resp = client.post(href, headers = headers,json=body)
    assert resp.status_code == expect_code


def check_control_put_method(client, ctrl, obj, api_key = "", body = None, expect_code = 301):
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
    headers = {
        "Content-Type": "application/json; charset=utf-8;",
        "authenticate_key": api_key
    }
    if body == None:
        faker = JSF(schema)
        body = faker.generate()
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
