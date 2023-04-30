import requests 
import json 
from flask import Flask, render_template, redirect, url_for, jsonify , session, request, Markup
from flask_session import Session
from datetime import datetime 
from helper import generator
from threading import Thread
import time

SERVER_URL = "http://localhost:5000"

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

main_user_flag=0
second_user_flag=0
main_user_data=[]
second_user_data=[]


def threaded_task(matchinguser):
    global second_user_data
    global second_user_flag
    user= generator.find_user(s,matchinguser, body["@controls"]["plm:users-all"]["href"],SERVER_URL)
    playlistdata,playlist_hrefs = generator.display_playlists(s,user,SERVER_URL)
    second_user_data=generator.playlist_tracks(s,playlist_hrefs,SERVER_URL)
    second_user_flag=1


def threaded_task2(playlist_hrefs):
    global main_user_data
    global main_user_flag
    main_user_data=generator.playlist_tracks(s,playlist_hrefs,SERVER_URL)
    main_user_flag=1

# app
@app.route('/', methods = ['GET', 'POST'])  #the main index entry point to our app 
def landing():
   
    return render_template('landing.html')




@app.route('/playlists', methods = ['GET', 'POST'])  
def playlists():
    user=request.form['username']
    matchinguser=request.form['matchinguser'] 
    thread = Thread(target=threaded_task, args=(matchinguser,))
    thread.daemon = True
    thread.start()
    user= generator.find_user(s,user, body["@controls"]["plm:users-all"]["href"],SERVER_URL)
    data,playlist_hrefs = generator.display_playlists(s,user,SERVER_URL)
    thread2 = Thread(target=threaded_task2, args=(playlist_hrefs,))
    thread2.daemon = True
    thread2.start()
    session['users'] = [user,matchinguser]
    return render_template('playlists.html',data=data)

@app.route('/tracks', methods = ['GET', 'POST'])  
def tracks():
    global main_user_data
    global second_user_data
    global main_user_flag
    global second_user_flag

    while main_user_flag !=1 or second_user_flag !=1:
        pass
    main_user_flag = 0
    second_user_flag = 0

    return render_template('tracks.html',userdata=main_user_data,match_data=second_user_data,users=session.get('users'))

@app.route('/matching', methods = ['GET', 'POST'])  
def matching():
    results, percent = generator.match_tracks(main_user_data,second_user_data)
    
    return render_template('matching.html',data=results, percent = percent)

if __name__ == '__main__':
    with requests.Session() as s:
        resp = s.get(SERVER_URL + "/api/")
    if resp.status_code != 200:
        print("Unable to access API.")
    else:
        body = resp.json()
        print(body)
    app.run(debug=True, port=8080)

