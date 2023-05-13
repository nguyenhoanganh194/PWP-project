import requests
import json
from datetime import datetime

SERVER_URL = "http://localhost:5000"
if __name__ == "__main__":
    with requests.Session() as s:
        resp = s.get(SERVER_URL + "/api/playlist/ali/12/")
        body = resp.json()
        print(body)


        data={}
        data["name"]='random music'
        data["created_at"]= datetime.now()
        resp = s.request(
            'PUT',
            SERVER_URL +"/api/playlist/ali/12/",
            data=json.dumps(data, default= str),
            headers = {"Content-type": "application/json"}
        )
        body = resp.status_code
        print(body)

