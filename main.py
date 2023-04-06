import pandas as pd
import speech_recognition as sr
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth

from pepper import *

# Set variables from setup.txt
setup = pd.read_csv('setup.txt', sep='=', index_col=0, header=None).to_dict()[1]

# Connecting to the Spotify account
auth_manager = SpotifyOAuth(
    client_id=setup['client_id'],
    client_secret=setup['client_secret'],
    redirect_uri=setup['redirect_uri'],
    scope=setup['scope'],
    username=setup['username'])
spotify = sp.Spotify(auth_manager=auth_manager)

# Selecting device to play from
devices = spotify.devices()
deviceID = None
for d in devices['devices']:
    d['name'] = d['name'].replace('’', '\'')
    if d['name'] == setup['device_name']:
        deviceID = d['id']
        break

# Setup microphone and speech recognizer
r = sr.Recognizer()
m = None
input_mic = setup['input_device']
for i, microphone_name in enumerate(sr.Microphone.list_microphone_names()):
    if microphone_name == input_mic:
        m = sr.Microphone(device_index=i)

print('listening...')
while True:
    with m as source:
        r.adjust_for_ambient_noise(source=source)
        audio = r.listen(source=source)

    command = None
    try:
        command = r.recognize_google(audio_data=audio).lower()
    except sr.UnknownValueError:
        continue

    print(command)
    words = command.split()
    if len(words) <= 1:
        print('Could not understand. Try again')
        continue

    name = ' '.join(words[1:])
    try:
        if words[0] == 'album':
            uri = get_album_uri(spotify=spotify, name=name)
            play_album(spotify=spotify, device_id=deviceID, uri=uri)
        elif words[0] == 'artist':
            uri = get_artist_uri(spotify=spotify, name=name)
            play_artist(spotify=spotify, device_id=deviceID, uri=uri)
        elif words[0] == 'song':
            uri = get_track_uri(spotify=spotify, name=name)
            play_track(spotify=spotify, device_id=deviceID, uri=uri)
        elif words[0] == 'playlist':
            uri = get_playlist_uri(spotify=spotify, name=name)
            play_playlist(spotify=spotify, device_id=deviceID, uri=uri)
        else:
            print('Specify either "album", "artist" or "play". Try Again')
    except InvalidSearchError:
        print('InvalidSearchError. Try Again')
