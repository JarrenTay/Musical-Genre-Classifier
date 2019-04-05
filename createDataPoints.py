import spotipy
import spotipy.util as util
import sys
import heapq
import subprocess
from getpass import getpass

#read ssh file to get username, client_id, and client_secret

info = open('ssh', 'r')
username = info.readline()[:-1]
clientId = info.readline()[:-1]
clientSecret = info.readline()[:-1]
redirect = info.readline()[:-1]
#password = getpass()

scope = 'user-library-read app-remote-control streaming'

token = util.prompt_for_user_token(username,scope,client_id=clientId,client_secret=clientSecret,redirect_uri=redirect)

if token:
    print 'Success!'
else:
    print('Failed...')

spotify = spotipy.Spotify(auth=token)

playlistList = open('playlistList.txt', 'r')

line = playlistList.readline()[:-1]
lineList = line.split(',')
category = lineList[0]
infoList = lineList[1].split(':')
userId = infoList[2]
playlistId = infoList[4]

playlist = spotify.user_playlist_tracks(userId, playlistId)
numTracks = playlist['total']
tracks = playlist['items']

trackId = tracks[int(sys.argv[1])]['track']['id']
print trackId

aa = spotify.audio_analysis(trackId)
track = spotify.track(trackId)
print track['name']

posToNote = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}
posToNote2 = {0: 'C', 1: 'c', 2: 'D', 3: 'd', 4: 'E', 5: 'F', 6: 'f', 7: 'G', 8: 'g', 9: 'A', 10: 'a', 11: 'B'}

# C, C#, D, D#, E, F, F#, G, G#, A, A#, B
# Chorus is usually around 25% of the songs duration
# Let's determine this time, and give a 5% leniency for segment timing.
# Cap the chorus at 25 seconds.
# Create datapoints that that has a starting note (one-hot encoded), four ints that describe increase or decrease in pitch, the timbre of the first note, and the key of the song.

