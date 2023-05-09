import difflib
import json
import requests 

def playlist_tracks(s, playlist_track_href,SERVER_URL):
    """
    a helper function used by the main display_playlists function
    input params:session, playlisttrackitem URI name server url
    output: returns playlist track item data 
    """
    
    data=[]
    for single_href in playlist_track_href:
        resp = s.get(SERVER_URL + single_href)
        body = resp.json()
        collection=body["items"]        
        for item in collection:
            track=[]
            resp = s.get(SERVER_URL + item["@controls"]["self"]["href"])
            body = resp.json()
            resp = s.get(SERVER_URL + body["@controls"]["track"]["href"])
            body = resp.json()
            track.append(body["item"]["name"])
            track.append(body["item"]["artist"])
            track.append(body["item"]["duration"])
            data.append(track)
    return data



def display_playlists(s,user_href,SERVER_URL):
    """
    generate a list of the user playlists with all its data 
    input params: session, user URI, and the API server URl
    output: user playlist data, the playlist URI, the tracks URI
    """
    resp = s.get(SERVER_URL + user_href)
    body = resp.json()
    playlists_href=body["@controls"]["plm:playlists-of"]["href"]
    tracks_href= body["@controls"]["plm:tracks-of"]["href"]
    data =[]
    playlist_hrefs=[]
    resp = s.get(SERVER_URL + playlists_href)
    body = resp.json()
    collection=body["items"]
    for item in collection:
        resp = s.get(SERVER_URL + item["@controls"]["self"]["href"])
        body = resp.json()
        item_data=[]
        playlist_hrefs.append(body["@controls"]["plm:tracks_of_playlist"]["href"])
        item_data.append(body["item"]["name"])
        item_data.append(body["item"]["created_at"])
        item_data.append(body["@controls"]["self"]["href"])
        data.append(item_data)
    
    return data,playlist_hrefs,tracks_href 

def find_user_href(name, collection):
    """
    a helper function used by the main find_user function
    input params: name and UserCollection URI
    output: returns the user URI
    """

    hits = []
    for item in collection:
        if item["@controls"]["name"]["href"] ==name:
            hits.append(item)
    if len(hits) == 1:
        return hits[0]["@controls"]["self"]["href"]
    elif len(hits) >= 2:
        print("error")
    else:
        return None


def find_user(s,user, users_href,SERVER_URL):
    """
    find the user URI 
    input params: session, user name, the UerCollection URI, the API server URl
    output: returns the user URI
    """
    resp = s.get(SERVER_URL + users_href)
    body = resp.json()
    user_href = find_user_href(user, body["items"])
    return user_href

def match_tracks(main_user_data,second_user_data):
    """
    a helper function to calcluate the similarity between tracks 
    input params: arrays of user data from both main user and second uer 
    output: returns a list of common tracks and percent of matching
    """
    list =[]
    for main_user_item in main_user_data:      
        name=main_user_item[0]
        for second_user_item in second_user_data:
            seq = difflib.SequenceMatcher(None,name,second_user_item[0])
            if (seq.ratio()*100) >88:
                list.append(main_user_item)
                break 
    percent = len(list)/len(main_user_data) *100         
    return list, round(percent)


def add_track(s, ctrl,trackdata,SERVER_URL):
    """
    a helper function used to add each track to user playlist
    input params:session, ctrl methods, trackitem data and server url
    output: returns the response of request headers uri location
    """
    data = {}
    data["name"]=trackdata[0]
    data["artist"]=trackdata[1]
    data["duration"]=trackdata[2]
    resp = s.request(
        ctrl["method"],
        SERVER_URL + ctrl["href"],
        data=json.dumps(data),
        headers = {"Content-type": "application/json"}
    )
    return resp.headers["Location"]


def add_track_to_playlist(s,locations,playlisthref,SERVER_URL):
    """
    a function used to add tracks to user playlist
    input params:session, a list of tracks URIs, playlist URI and server url
    output: returns the user URI
    """
    list=[]
    for item in locations:
        resp = s.get(SERVER_URL + item)
        body = resp.json()
        list.append(body["item"]["id"])
    
    response = s.get(SERVER_URL + playlisthref)
    body = response.json()
    id = body["item"]["id"]
    tracks_of_playlist =body["@controls"]["plm:tracks_of_playlist"]["href"]

    response = s.get(SERVER_URL + tracks_of_playlist)
    body = response.json()
    ctrl= body["@controls"]["plm:add-playlisttrack"]

    for track in list:
        data = {}
        data["track_id"]=track
        data["playlist_id"]=id
        data["track_number"]=track
        resp = s.request(
            ctrl["method"],
            SERVER_URL + ctrl["href"],
            data=json.dumps(data),
            headers = {"Content-type": "application/json"}
        )

def get_recommendations(user,SERVICE_URL):
    """
    a function used to communicate with the service to get recommendations
    input params:user name, and service url
    output: returns the user URI
    """
    with requests.Session() as s:
        resp = s.get(SERVICE_URL + "/api/")
        if resp.status_code != 200:
            print("Unable to access API.")
        else:
            body = resp.json()
            resp = s.get(SERVICE_URL + body['@controls']['lm:users-all']['href'])
            body = resp.json()
            for item in body['items']:                
                if item['name'] == user:
                    user_recommendation_href =item['@controls']['lm:RecommendationList']['href']
            resp = s.get(SERVICE_URL + user_recommendation_href)
            body = resp.json()
    return body['items']
