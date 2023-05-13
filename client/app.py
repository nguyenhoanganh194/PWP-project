import requests
from flask import Flask, render_template, session, request
from flask_session import Session
from helper import generator
from threading import Thread

SERVER_URL="http://localhost:5000"
SERVICE_URL="http://localhost:3000"
app=Flask(__name__)
app.config["SESSION_TYPE"]="filesystem"
Session(app)
main_user_flag=0
second_user_flag=0
recommendations_flag=0
main_user_data=[]
second_user_data=[]
main_user_playlists=[]
recommendation_list=[]

def threaded_task(matchinguser):
    '''
    This threaded task is mainly for extracting the second user data including playlists, tracks
    it is used to match these data with the main user data
    input params: the name of the second user
    error handling: the eeror handling for wrong names is not carried out through this thread,
    the error is handled by the palylist function 
    '''
    global second_user_data
    global second_user_flag
    playlistdata,playlist_hrefs,tracks_href = generator.display_playlists(s,matchinguser,SERVER_URL)
    second_user_data=generator.playlist_tracks(s,playlist_hrefs,SERVER_URL)
    second_user_flag=1


def threaded_task2(playlist_hrefs):
    '''
    This threaded task is mainly for extracting the playlist data of the main user
    input params: the URI of the PlaylistCollection of the user
    error handling: the error handling is not carried out through this thread,
    the error is handled by the palylist function 
    '''
    global main_user_data
    global main_user_flag
    main_user_data=generator.playlist_tracks(s,playlist_hrefs,SERVER_URL)
    main_user_flag=1

def service_task(user):
    '''
    This threaded task is used to call the Auxiliary service to start functioning
    input params: the name of the user we want to generate recommendations for 
    error handling: the error handling is carried by the service itself
    '''
    global recommendations_flag
    global recommendation_list
    recommendation_list= generator.get_recommendations(user,SERVICE_URL)
    recommendations_flag=1



# app
@app.route('/', methods = ['GET', 'POST'])
def landing():
    """
    the main index entry point to our app 
    """
    return render_template('landing.html')




@app.route('/playlists', methods = ['GET', 'POST'])
def playlists():
    """
    the playlist entry point is used to display all the users playlists and data about each playlist 
    """
    global main_user_playlists
    username=request.form['username']
    matchingusername=request.form['matchinguser']
    user= generator.find_user(s,username, body["@controls"]["plm:users-all"]["href"],SERVER_URL)
    matchinguser= generator.find_user(s,matchingusername,\
                                       body["@controls"]["plm:users-all"]["href"],SERVER_URL)
    #this part is responsible for error handling and redirecting the user to error page
    if user == None or matchinguser == None:
        return render_template('error.html')
    else:
        #starting the thread for getting matched user data
        thread = Thread(target=threaded_task, args=(matchinguser,))
        thread.daemon = True
        thread.start()
        main_user_playlists,playlist_hrefs,tracks_href = \
            generator.display_playlists(s,user,SERVER_URL)
        #starting the thread for getting main user tracks
        thread2 = Thread(target=threaded_task2, args=(playlist_hrefs,))
        thread2.daemon = True
        thread2.start()
        session['users'] = [username,matchingusername]
        session['tracks_href'] = tracks_href
        session['playlist_hrefs']= [playlist_hrefs]
        return render_template('playlists.html',data=main_user_playlists)

@app.route('/tracks', methods = ['GET', 'POST'])
def tracks():
    """
    the tracks entry point is used to display all the user and other user tracks and data about each
    """
    global main_user_flag
    global second_user_flag

    while main_user_flag !=1 or second_user_flag !=1:
        pass
    main_user_flag = 0
    second_user_flag = 0

    users =session.get('users')
    #starting the service thread
    thread = Thread(target=service_task, args=(users[0],))
    thread.daemon = True
    thread.start()

    return render_template('tracks.html',\
                           userdata=main_user_data,match_data=second_user_data,users=users)

@app.route('/matching', methods = ['GET', 'POST'])
def matching():
    """
    the matching entry point is used to display the user and other user matching score
    """
    results, percent = generator.match_tracks(main_user_data,second_user_data)
    users =session.get('users')
    return render_template('matching.html',data=results, percent = percent,users=users)

@app.route('/addtrack', methods = ['GET', 'POST'])
def addtrack():
    """
    the add track entry point is used by the main user to
    add music from the other user to his own playlist
    """
    return render_template('addtrack.html',\
                           data=second_user_data,playlist_data=main_user_playlists)

@app.route('/tracksuccess', methods = ['GET', 'POST'])
def tracksuccess():
    """
    the track success entry point is displayed when tracks are added successfully to the palylist
    """
    track=request.form.getlist('track-name')
    playlisthref=request.form['playlist-href']
    response = s.get(SERVER_URL + session.get('tracks_href'))
    body = response.json()
    ctrl=body["@controls"]["plm:add-track"]
    trackdata=[]
    for item in track:
        for data in second_user_data:
            if item == data[0]:
                trackdata.append(data)
    locations =[]
    for item in trackdata:
        response = generator.add_track(s,ctrl,item,SERVER_URL)
        locations.append(response)

    generator.add_track_to_playlist(s,locations,playlisthref,SERVER_URL)

    return render_template('final.html')


@app.route('/recommendations', methods = ['GET', 'POST'])
def recommendations():
    """
    display the recommendations generated by the service
    """
    global recommendations_flag
    while recommendations_flag !=1:
        pass
    recommendations_flag = 0
    return render_template('recommendations.html',data=recommendation_list)



@app.route('/editplaylist', methods = ['GET', 'POST'])
def editplaylist():
    """
    edit a playlist of user 
    """

    return render_template('editplaylist.html',data=main_user_playlists,trackdata=main_user_data)


@app.route('/editsuccess', methods = ['GET', 'POST'])
def editsuccess():
    """
    edit successfull 
    """
    playlistdelete =request.form['playlist-delete']
    if playlistdelete != '':
        response = generator.deleteplaylist(s,playlistdelete,SERVER_URL)

    playlistedit =request.form['playlist-edit']
    playlistname =request.form['playlistname']
    if playlistedit != '':
        generator.editplaylist(s,playlistname,playlistedit,SERVER_URL)    

    trackdelete =request.form['track-delete']

    if trackdelete != '':
        response = generator.deletetrack(s,trackdelete,SERVER_URL)    

    return render_template('libraryedit.html')




if __name__ == '__main__':
    with requests.Session() as s:
        resp = s.get(SERVER_URL + "/api/")
    if resp.status_code != 200:
        print("Unable to access API.")
    else:
        body = resp.json()
    app.run(debug=True, port=8080)
