import pytest
import json

from app import app

app = app.test_client()

def test_index_route():
    resp = app.get('/api/')
    assert resp.status_code == 200
    body = json.loads(resp.data)
    check_namespace(body,'/lyricsmatcher/link-relations/')
    check_control(app,"lm:users-all", body)


class TestUserCollection(object):
    RESOURCE_URL = "/api/users/"

    def test_get_collection(self):
        resp = app.get(self.RESOURCE_URL)
        print(resp)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        check_namespace(body,'/lyricsmatcher/link-relations/')
        check_control(app,"self",body)
        item = body["items"][0]
        check_control(app,"lm:RecommendationList",item)
        assert item['name'] == 'User1'

class TestRecommendationList(object):
    RESOURCE_URL = '/api/RecommendationList/'

    def test_get_collection(self):
        resp = app.get(self.RESOURCE_URL + 'User1/')
        assert resp.status_code == 200
        body = json.loads(resp.data)
        check_namespace(body,'/lyricsmatcher/link-relations/')
        check_control(app,"self",body)
        items = body["items"]
        assert len(items) == 0
        assert type(items) is list

        resp = app.get(self.RESOURCE_URL + 'ali/')
        assert resp.status_code == 200
        body = json.loads(resp.data)
        items = body["items"]
        assert len(items) > 0
        assert type(items) is list
        assert type(items[0]) is list
        assert type(items[0][0]) is str






def check_namespace(body,namespace):
    """
    Checks that the namespace is found from the response body, and its "name" attribute.
    """
    ns_href = body["@namespaces"]["lm"]["name"]
    assert ns_href == namespace

def check_control(client, ctrl, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """
    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200