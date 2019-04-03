import spotipy
import spotipy.util as util
import sys
from getpass import getpass

#read ssh file to get username, client_id, and client_secret

info = open('ssh', 'r')
username = info.readline()[:-1]
clientId = info.readline()[:-1]
clientSecret = info.readline()[:-1]
redirect = info.readline()[:-1]
password = getpass()

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

trackId = tracks[0]['track']['id']
print trackId

#spotify.start_playback()
aa = spotify.audio_analysis(trackId)
#print aa['sections']
#print len(aa['sections'])

for seg in aa['segments']:
	#for num in xrange(12):
	#	if seg['pitches'][num] == 1.0:
	#		print num
	#		break
	print seg['timbre']
	
# C, C#, D, D#, E, F, F#, G, G#, A, A#, B
