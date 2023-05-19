import json
import requests
import base64
from flask import Blueprint,flash, redirect, render_template, session, request
from werkzeug.exceptions import Unauthorized
from music_api.forms import DeleteForm, LoginForm, PlaylistForm, SearchSongsForm, FindSongForm
from music_api.helpers import first, get_random_search, search_videos, my_spotify_client
from music_api.models import Playlist, PlaylistSong, Song, User, db
import io
import soundfile as sf
from pydub import AudioSegment
import base64
import numpy as np
import librosa
import wave
import soundfile

site = Blueprint('site', __name__, template_folder='site_templates')

@site.route("/")
def homepage():
    """Show homepage with links to site areas."""
    return redirect("/register")

@site.route("/playlist")
def playlist_redirect():
    """Show homepage with links to site areas."""
    id = session["user_id"]
    user = User.query.get_or_404(id)
    print(122222222222,user)
    # session["user_id"] = user.id  
    return redirect(f"/users/profile/{user.id}")



#Home Page
@site.route('/users/home/<int:id>', methods=["GET", "POST"])
def user_home(id):
    """Show form that searches new form, and show results"""
    if "user_id" not in session or id != session['user_id']:
        flash("You must be logged in to view!")
        return redirect("/login")
    else:
        id = session["user_id"]
        user = User.query.get_or_404(id)
        form = SearchSongsForm()
        resultsSong = []
        youtube_results = []
        checkbox_form = request.form
        random_search, random_offset = get_random_search()
        
        api_call_track = my_spotify_client.search(random_search,'track', random_offset)   
        if api_call_track:
            # get search results, don't inclue songs that are on playlist already
            for item in api_call_track['tracks']['items']:
                images = [ image['url'] for image in item['album']['images'] ]
                artists = [ artist['name'] for artist in item['artists'] ]
                urls = item['album']['external_urls']['spotify']
                resultsSong.append({
                    'title' : item['name'],
                    'spotify_id': item['id'],
                    'album_name': item['album']['name'], 
                    'album_image': first(images,''),
                    'artists': ", ".join(artists),
                    'url': urls
                })
        

        

        if form.validate_on_submit() and checkbox_form['form'] == 'search_songs': 
            track_data = form.track.data
            api_call_track = my_spotify_client.search(track_data,'track')   
            youtube_results = search_videos(track_data)

            # get search results, don't inclue songs that are on playlist already
            for item in api_call_track['tracks']['items']:
                images = [ image['url'] for image in item['album']['images'] ]
                artists = [ artist['name'] for artist in item['artists'] ]
                urls = item['album']['external_urls']['spotify']
                resultsSong.append({
                    'title' : item['name'],
                    'spotify_id': item['id'],
                    'album_name': item['album']['name'], 
                    'album_image': first(images,''),
                    'artists': ", ".join(artists),
                    'url': urls
                })


        # search results checkbox form
        if 'form' in checkbox_form and checkbox_form['form'] == 'pick_songs':
            list_of_picked_songs = checkbox_form.getlist('track')
            # map each item in list of picked songs
            jsonvalues = [ json.loads(item) for item in  list_of_picked_songs ]


            for item in jsonvalues:
                title = item['title']
                spotify_id = item['spotify_id']
                album_name = item['album_name']
                album_image = item['album_image']
                artists = item['artists']
                new_songs = Song(title=title, spotify_id=spotify_id, album_name=album_name, album_image=album_image, artists=artists)
                db.session.add(new_songs)
                db.session.commit()
                # add new song to its playlist
                # playlist_song = PlaylistSong(song_id=new_songs.id, playlist_id=playlist_id)
                # db.session.add(playlist_song)
                # db.session.commit()
    
            # return redirect(f'/playlists/{playlist_id}')
        def serialize(obj):
            return json.dumps(obj)
        
        
        return render_template('users/home.html', form=form, resultsSong=resultsSong, youtube_results=youtube_results, serialize=serialize, user=user)

@site.route('/users/find-songs/<int:id>', methods=['GET', 'POST'])
def find_songs(id):
    if "user_id" not in session or id != session['user_id']:
        flash("You must be logged in to view!")
        return redirect("/login")
    else:
        id = session["user_id"]
        user = User.query.get_or_404(id)
        result = None
        if request.method == 'POST':
            audio_file = request.files['audio']
            audio_data = audio_file.read()
            tmp = io.BytesIO(audio_data)
            data,   sr = sf.read(tmp)
            # Save audio file with soundfile of 16 bit pcm little endian
            sf.write('audio.wav', data, sr, subtype='PCM_16')
            
            print(sr)
            y,s = librosa.load('audio.wav', sr=44100)
            print(s)
            sf.write('audio44.wav', y, s, subtype='PCM_16')
    
            wav_file = wave.open("audio44.wav", "rb")
            # save y as wav file
            # librosa.output.write_wav('audio_files/new1.wav', y, s)
            data = np.frombuffer(wav_file.readframes(wav_file.getnframes()), dtype=np.int16)
            assert data.dtype == np.int16, 'Bad sample type: %r' % data.dtype
            base64_string = base64.b64encode(data)
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            bit_depth = wav_file.getsampwidth() // 8
            print(222,sample_rate,channels,bit_depth)
            wav_file.close()
            payload = base64_string.decode()
            headers = {
                "content-type": "text/plain",
                "X-RapidAPI-Key": "74bfefe667msh04af17251b4fc25p1b1813jsn720154ddf0e4",
                "X-RapidAPI-Host": "shazam.p.rapidapi.com"
            }

            print(payload[:100])
            url = "https://shazam.p.rapidapi.com/songs/detect"

            
            response = requests.post(url, data=payload, headers=headers)
            response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
            result = response.json()
            print(12222)
            return result
            
        return render_template('users/find-songs.html', user=user, result=result)


@site.route('/users/find-song/<int:id>', methods=['GET', 'POST'])
def find_song(id):
    if "user_id" not in session or id != session['user_id']:
        flash("You must be logged in to view!")
        return redirect("/login")
    else:
        id = session["user_id"]
        user = User.query.get_or_404(id)
        form = FindSongForm()
        data = {}

        if form.validate_on_submit():
            song = form.song.data
            url = "https://shazam.p.rapidapi.com/search"
            querystring = {"term":song,"locale":"en-US","offset":"0","limit":"5"}
            headers = {
                'x-rapidapi-host': "shazam.p.rapidapi.com",
                'x-rapidapi-key': "74bfefe667msh04af17251b4fc25p1b1813jsn720154ddf0e4"
            }
            
            try:
                response = requests.request("GET", url, headers=headers, params=querystring)
                response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
                
                data = response.json()
                # Verify if the response contains the expected structure
                if not 'tracks' in data or not 'hits' in data['tracks']:
                    flash('Unexpected API response', 'error')
                    data = {}
                    
            except requests.exceptions.RequestException as err:
                flash(f'An error occurred: {err}', 'error')
            
        return render_template('users/find-song.html', form=form, data=data, user=user)

@site.route("/users/profile/<int:id>",  methods=["GET", "POST"])
def profile(id):
    """Example hidden page for logged-in users only."""

    # raise 'here'
    if "user_id" not in session or id != session['user_id']:
        flash("You must be logged in to view!")
        return redirect("/login")
    else:
        id = session["user_id"]
        user = User.query.get_or_404(id)
        form = PlaylistForm()
        user = User.query.get_or_404(id)
        playlists = Playlist.query.filter_by(user_id=id).all()
        if form.validate_on_submit(): 
            name = form.name.data
            new_playlist = Playlist(name=name, user_id=session['user_id'])
            db.session.add(new_playlist)
            db.session.commit()
            playlists.append(new_playlist)
            return redirect(f"/users/profile/{id}")
        return render_template("users/profile.html", playlists=playlists, form=form, user=user)




@site.route("/playlists/<int:playlist_id>", methods=['POST', 'GET'])
def show_playlist(playlist_id):
    """Show detail on specific playlist."""
    playlist = Playlist.query.get_or_404(playlist_id)
    if "user_id" not in session or  playlist.user_id != session['user_id']:
        flash("You must be logged in to view!")
        return redirect("/login")
    
    songs = PlaylistSong.query.filter_by(playlist_id=playlist_id)
    form = request.form
    if request.method == 'POST' and form['remove'] and form['song']:
        song_id = form['song']
        song_to_delete = PlaylistSong.query.get(song_id)
        db.session.delete(song_to_delete)
        # raise 'here'
        db.session.commit()
    return render_template("playlist/playlist.html", playlist=playlist, songs=songs)


@site.route('/playlists/<int:playlist_id>/search', methods=["GET", "POST"])
def show_form(playlist_id):
    """Show form that searches new form, and show results"""
    playlist = Playlist.query.get(playlist_id)
    play_id  = playlist_id
    form = SearchSongsForm()
    resultsSong = []
    youtube_results = []
    checkbox_form = request.form

    list_of_songs_spotify_id_on_playlist = []
    for song in playlist.songs:
      list_of_songs_spotify_id_on_playlist.append(song.spotify_id)
    songs_on_playlist_set = set(list_of_songs_spotify_id_on_playlist)
    

    if form.validate_on_submit() and checkbox_form['form'] == 'search_songs': 
        track_data = form.track.data
        api_call_track = my_spotify_client.search(track_data,'track')   
        youtube_results = search_videos(track_data)

        # get search results, don't inclue songs that are on playlist already
        for item in api_call_track['tracks']['items']:
          if item['id'] not in songs_on_playlist_set:
            images = [ image['url'] for image in item['album']['images'] ]
            artists = [ artist['name'] for artist in item['artists'] ]
            urls = item['album']['external_urls']['spotify']
            resultsSong.append({
                'title' : item['name'],
                'spotify_id': item['id'],
                'album_name': item['album']['name'], 
                'album_image': first(images,''),
                'artists': ", ".join(artists),
                'url': urls
            })


    # search results checkbox form
    if 'form' in checkbox_form and checkbox_form['form'] == 'pick_songs':
        list_of_picked_songs = checkbox_form.getlist('track')
        # map each item in list of picked songs
        jsonvalues = [ json.loads(item) for item in  list_of_picked_songs ]


        for item in jsonvalues:
            title = item['title']
            spotify_id = item['spotify_id']
            album_name = item['album_name']
            album_image = item['album_image']
            artists = item['artists']
            new_songs = Song(title=title, spotify_id=spotify_id, album_name=album_name, album_image=album_image, artists=artists)
            db.session.add(new_songs)
            db.session.commit()
            # add new song to its playlist
            playlist_song = PlaylistSong(song_id=new_songs.id, playlist_id=playlist_id)
            db.session.add(playlist_song)
            db.session.commit()
  
        return redirect(f'/playlists/{playlist_id}')
    def serialize(obj):
        return json.dumps(obj)
    
    
    return render_template('song/search_new_songs.html', playlist=playlist, form=form, resultsSong=resultsSong, youtube_results=youtube_results, serialize=serialize)

@site.route('/play/<int:song_id>', methods=["GET"])
def play_song(song_id):
    """Play song."""
    return render_template('s.html', song_id=song_id)

@site.route("/playlists/<int:playlist_id>/update", methods=["GET", "POST"])
def update_playlist(playlist_id):
    """Show update form and process it."""
    playlist = Playlist.query.get(playlist_id)
    if "user_id" not in session or playlist.user_id != session['user_id']:
        flash("You must be logged in to view!")
        return redirect("/login")
    form = PlaylistForm(obj=playlist)
    if form.validate_on_submit():
        playlist.name = form.name.data
        db.session.commit()
        return redirect(f"/users/profile/{session['user_id']}")
    return render_template("/playlist/edit.html", form=form, playlist=playlist)



@site.route("/playlists/<int:playlist_id>/delete", methods=["POST"])
def delete_playlist(playlist_id):
    """Delete playlist."""

    playlist = Playlist.query.get(playlist_id)
    if "user_id" not in session or playlist.user_id != session['user_id']:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(playlist)
        db.session.commit()

    return redirect(f"/users/profile/{session['user_id']}")
