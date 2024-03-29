from flask import Flask, jsonify, send_file, request
from werkzeug.utils import secure_filename
from io import BytesIO
from mutagen.id3 import ID3
import requests
import os
import threading
from time import sleep

app = Flask(__name__)

res_data = {}
res_data2 = {}
# {'Blues': 'Watch Yourself.mp3', 'Lofi': 'Late Night Call.mp3',
# 'Persian Rap': 'Rockstar (feat. Sadegh).mp3', 'Phonk': 'Nightmare City.mp3',
# 'Pop': 'Nonsense.mp3', 'Hip-Hop': 'Do For Love.mp3', 'Rock': 'Self Esteem.mp3'}
paths = {
    "blues": "./blues",
    "prap": "./prap",
    "hiphop": "./hip",
    "lofi": "./lofi",
    "pop": "./pop",
    "rock": "./rock",
    "phonk": "./phonk"
}


def update_data():
    global res_data
    r = requests.get('http://127.0.0.1:15210/status-json.xsl')
    #print(r.json())
    for i in r.json()["icestats"]["source"]:
        try:
            res_data[i["genre"]] = i["title"]
            res_data2[i["genre"]] = i["artist"]
        except:
            ...


def get_path(music_name):
    for root, dirs, files in os.walk(r'.'):
        for name in files:
            if music_name in name:
                return os.path.abspath(os.path.join(root, name))
    #print("not found")


def get_img(genre):
    #print(res_data[genre])
    song_path = get_path(res_data[genre])
    tags = ID3(song_path)
    #print(tags.pprint())
    pict = tags.getall('APIC')[0].data
    return BytesIO(pict)


def get_meta(genre):
    title = res_data[genre]
    artist = res_data2[genre]
    if genre == "prap":
        return "", "", "", "", artist, title
    song_path = get_path(res_data[genre])
    tags = ID3(song_path)

    text = ""
    text_ = tags.getall('USLT')
    if text_:
        text = str(text_[0])

    spotify = ""
    spotify_ = tags.getall('WOAS')
    if spotify_:
        spotify = str(spotify_[0])

    time = 0
    time_ = tags.getall('TDRC')
    if time_:
        time = str(time_[0])

    link = ""
    for i in tags.getall('COMM'):
        if "https" in str(i):
            link = str(i)

    return text, time, link, spotify, artist, title


@app.route('/img')
def download_file():
    genre = request.args.get("genre")
    if genre not in paths:
        return jsonify(error="notfound"), 404
    #print(get_img(genre))
    if genre == "prap":
        return send_file("prap.jpg")
    try:
        return send_file(get_img(genre), mimetype='png')
    except:
        return jsonify(error="500"),400

@app.route('/meta')
def metadata():
    genre = request.args.get("genre")
    if genre not in paths:
        return jsonify(error="notfound"), 404
    text, time, link, spotify, artist, title = get_meta(genre)
    return jsonify(text=text, time=time, link=link, spotify=spotify, artist=artist, title=title)


def loop():
    while 1:
        sleep(5)
        try:
            update_data()
        except Exception as e:
            print(e)
            exit()


def run_loop():
    loop_ = threading.Thread(target=loop)
    loop_.start()


#run_loop()
app.run("0.0.0.0")
