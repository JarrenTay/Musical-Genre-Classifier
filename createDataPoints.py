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

trackId = tracks[9]['track']['id']
print trackId

#spotify.start_playback()
aa = spotify.audio_analysis(trackId)
#print aa['sections']
#print len(aa['sections'])

secLoudness = -100.0
numSecs = len(aa['sections'])
for x in xrange(numSecs):
	print aa['sections'][x]['start']
	if x < (numSecs * 2 / 3):
		if secLoudness < aa['sections'][x]['loudness']:
			loudestSec = aa['sections'][x]

loudSecBegin = loudestSec['start'] - 3
loudSecEnd = loudSecBegin + loudestSec['duration'] + 6

print loudSecBegin, loudSecEnd

count = 0
for seg in aa['segments']:
	if seg['start'] > loudSecBegin and seg['start'] < loudSecEnd:
		count = count + 1
		print seg['pitches']
	#print seg['timbre']
print count
# C, C#, D, D#, E, F, F#, G, G#, A, A#, B
# lots of info here. What do we want?
# We have number of segments
# we have note chroma of each note
# We have timbre of each note
# We have time between each note

# Basic notes: 5 notes, 4 times, 3 timbres per note? => 24 dimensions per data point
# High bpm 2:36 song has 787 segments. 782 points. Thats a lot of points per song

# Use loudest section? Loudest section was 50 secs. had 175 segments. 