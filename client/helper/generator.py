import difflib

def playlist_tracks(s, playlist_track_href,SERVER_URL):
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

    """
    resp = s.get(SERVER_URL + user_href)
    body = resp.json()
    playlists_href=body["@controls"]["plm:playlists-of"]["href"]
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
        data.append(item_data)
    
    return data,playlist_hrefs 

def find_user_href(name, collection):
    hits = []
    for item in collection:
        if item["@controls"]["name"]["href"] ==name:
            hits.append(item)
    if len(hits) == 1:
        return hits[0]["@controls"]["self"]["href"]
    elif len(hits) >= 2:
        #return prompt_artist_choice(name, hits)["@controls"]["self"]["href"]
        print("error")
    else:
        return None


def find_user(s,user, users_href,SERVER_URL):
    resp = s.get(SERVER_URL + users_href)
    body = resp.json()
    user_href = find_user_href(user, body["items"])
    return user_href

def match_tracks(main_user_data,second_user_data):
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
