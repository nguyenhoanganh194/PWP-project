import json
import requests
from datetime import datetime
from flask import Flask, Response, request
from flask.cli import with_appcontext
from flask_restful import Resource, Api
from werkzeug.exceptions import BadRequest, NotFound, ServiceUnavailable
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, OperationalError
import time
import pandas as pd

app = Flask(__name__)
api = Api(app)



Main_API_SERVER="http://localhost:5000"
API_NAME = "lyricsmatcher"
MASON = "application/vnd.mason+json"
NAMESPACE_SHORT = "lm"
LINK_RELATIONS_URL = "/{}/link-relations/".format(API_NAME)
TRACK_PROFILE = "/profiles/track/"


data= pd.read_csv("Spotify_final_dataset.csv")
data['Artist Name'] = data['Artist Name'].str.strip()


def get_users():
    """
    a function used to aget the URI of User Collection of main API
    output: returns a list of users data from the main API
    """
    with requests.Session() as s:
        resp = s.get(Main_API_SERVER + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()          
            resp = s.get(Main_API_SERVER + body["@controls"]["plm:users-all"]["href"])
            body = resp.json()
            collection= body["items"]
            hits = []
            for item in collection:
                hits.append(item["@controls"]["name"]["href"])
            return hits
        
def get_href(user):
    """
    a function used to get the URI of a specifi user
    input params:user name
    output: returns the user URI
    """
    with requests.Session() as s:
        resp = s.get(Main_API_SERVER + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()          
            resp = s.get(Main_API_SERVER + body["@controls"]["plm:users-all"]["href"])
            body = resp.json()
            collection= body["items"]
            hits = []
            for item in collection:
                if item["@controls"]["name"]["href"] == user:
                    hits.append(item)   
            return s, hits[0]["@controls"]["self"]["href"]

def get_track_data(s, user_href):
    """
    a function used to extract all the tracks of a user
    input params:session, user URI 
    output: returns a list of artist names listed to by the user
    """
    resp = s.get(Main_API_SERVER + user_href)
    body = resp.json()
    tracks_href=body["@controls"]["plm:tracks-of"]["href"]
    resp = s.get(Main_API_SERVER + tracks_href)
    body = resp.json()
    collection=body["items"]
    tracks=[]
    artists=[]
    for item in collection:
        resp = s.get(Main_API_SERVER + item["@controls"]["self"]["href"])
        body = resp.json()
        tracks.append(body["item"]["name"])
        artists.append(body["item"]["artist"])

    return artists, tracks

def get_recommendations(artists):
    """
    a function used to generate recommendations based on artists names
    input params:a list of artists names 
    output: returns a list of artist music recommendations
    """
    recommendations = []
    for artist in artists:
        i=data[data['Artist Name']==artist]
        count =i['Song Name'].count()
        if count> 3:
            count=count*0.1
            round(count)
            count=int(count)
            for x in range(0,count):
                recommended_track=[]
                recommended_track.append(i['Artist Name'].values[x])
                recommended_track.append(i['Song Name'].values[x])
                recommendations.append(recommended_track)
    return recommendations

        
class RecommendationList(Resource):
    """
    The RecommendationList resource supports GET methods.
    Possible response codes:
    200 with a successful GET
    """
    def get(self,user):
        s, user_href=get_href(user)
        artists, tracks=get_track_data(s, user_href)
        recommendations = get_recommendations(artists)
        body = MasonBuilder()
        body.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        body.add_control("self", api.url_for(RecommendationList, user=user))
        body["items"] = recommendations
        return Response(json.dumps(body), 200, mimetype=MASON)



class UserCollection(Resource):
    """
    The UserCollection resource supports GET methods.
    Possible response codes:
    200 with a successful GET
    """

    def get(self):
        api_data=get_users()
        resp_data = MasonBuilder(
            items=[]
        )
        resp_data.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
        resp_data.add_control("self", api.url_for(UserCollection))
        for user in api_data:
            item = MasonBuilder(name=user)
            item.add_control( "lm:RecommendationList",api.url_for(RecommendationList,user=user))
            resp_data["items"].append(item)
        return Response(json.dumps(resp_data), 200, mimetype=MASON)






class MasonBuilder(dict):
    """
    A convenience class for managing dictionaries that represent Mason
    objects. It provides nice shorthands for inserting some of the more
    elements into the object but mostly is just a parent for the much more
    useful subclass defined next. This class is generic in the sense that it
    does not contain any application specific implementation details.
    """

    def add_error(self, title, details):
        """
        Adds an error element to the object. Should only be used for the root
        object, and only in error scenarios.

        Note: Mason allows more than one string in the @messages property (it's
        in fact an array). However we are being lazy and supporting just one
        message.

        : param str title: Short title for the error
        : param str details: Longer human-readable description
        """

        self["@error"] = {
            "@message": title,
            "@messages": [details],
        }

    def add_namespace(self, ns, uri):
        """
        Adds a namespace element to the object. A namespace defines where our
        link relations are coming from. The URI can be an address where
        developers can find information about our link relations.

        : param str ns: the namespace prefix
        : param str uri: the identifier URI of the namespace
        """

        if "@namespaces" not in self:
            self["@namespaces"] = {}

        self["@namespaces"][ns] = {
            "name": uri
        }

    def add_control(self, ctrl_name, href, **kwargs):
        """
        Adds a control property to an object. Also adds the @controls property
        if it doesn't exist on the object yet. Technically only certain
        properties are allowed for kwargs but again we're being lazy and don't
        perform any checking.

        The allowed properties can be found from here
        https://github.com/JornWildt/Mason/blob/master/Documentation/Mason-draft-2.md

        : param str ctrl_name: name of the control (including namespace if any)
        : param str href: target URI for the control
        """

        if "@controls" not in self:
            self["@controls"] = {}

        self["@controls"][ctrl_name] = kwargs
        self["@controls"][ctrl_name]["href"] = href

api.add_resource(RecommendationList, "/api/RecommendationList/<user>/")
api.add_resource(UserCollection, "/api/users/")

@app.route("/api/")
def entry():
    """
    the main and only entry point to our service
    """
    resp_data = MasonBuilder()
    resp_data.add_namespace(NAMESPACE_SHORT, LINK_RELATIONS_URL)
    resp_data.add_control(
        "lm:users-all",
        api.url_for(UserCollection)
    )
    return Response(json.dumps(resp_data), 200, mimetype=MASON)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)