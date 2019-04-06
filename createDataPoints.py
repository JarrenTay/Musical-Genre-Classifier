import spotipy
import spotipy.util as util
import sys
import subprocess
from getpass import getpass
import requests
import webbrowser
import json
import base64
import time

#read ssh file to get username, client_id, and client_secret

posToNote = {0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 4: 'E', 5: 'F', 6: 'F#', 7: 'G', 8: 'G#', 9: 'A', 10: 'A#', 11: 'B'}

info = open('ssh', 'r')
username = info.readline()[:-1]
clientId = info.readline()[:-1]
clientSecret = info.readline()[:-1]
redirect = info.readline()[:-1]

scope = 'user-library-read app-remote-control streaming'

spotifyAuth = spotipy.oauth2.SpotifyOAuth(clientId, clientSecret, redirect, None, scope)

URL = spotifyAuth.OAUTH_AUTHORIZE_URL
URL = URL + '?client_id=' + clientId
URL = URL + '&response_type=code'
URL = URL + '&redirect_uri=' + redirect
URL = URL + '&scope=' + scope
 
webbrowser.open(URL)
requestCodeURL = raw_input('Please enter the website URL that you were redirected to: \n')
requestCode = (requestCodeURL.split('='))[1]
URL = spotifyAuth.OAUTH_TOKEN_URL
PARAMS = {'grant_type': "authorization_code", 'code': requestCode, 'redirect_uri': redirect, 'client_id': clientId, 'client_secret': clientSecret}
r = requests.post(URL, PARAMS)
print r
responseDict = json.loads(r.text)
accessToken = responseDict['access_token']
tokenExpiration = responseDict['expires_in']
refreshToken = responseDict['refresh_token']
tokenRefreshed = time.time()

spotify = spotipy.Spotify(auth=accessToken)
playlistListFile = open('playlistList.txt', 'r')
playlistListRaw = playlistListFile.read()
playlistList = playlistListRaw.split('\n')

seenTracks = dict()

with open('data/musicPoints.data', 'w+') as dataFile:
    with open('data/musicPoints.labels', 'w+') as labelFile:
        for playlistRaw in playlistList:
            timeNow = time.time()
            if ((timeNow - tokenRefreshed) > (3600 - 300)):
                URL = spotifyAuth.OAUTH_TOKEN_URL
                PARAMS = {'grant_type': "refresh_token", 'refresh_token': refreshToken}
                HEADERS = {'Authorization': 'Basic ' + base64.standard_b64encode(clientId + ':' + clientSecret)}
                r = requests.post(URL, PARAMS, headers = HEADERS)
                print 'Reauthorizing Token'
                print r
                responseDict = json.loads(r.text)
                accessToken = responseDict['access_token']
                spotify = spotipy.Spotify(auth=accessToken)
                tokenRefreshed = timeNow
            lineList = playlistRaw.split(',')
            category = lineList[0]
            infoList = lineList[1].split(':')
            userId = infoList[2]
            playlistId = infoList[4]

            if category not in seenTracks:
                seenTracks[category] = set()

            playlist = spotify.user_playlist_tracks(userId, playlistId)
            numTracks = playlist['total']
            trackList = playlist['items']
            for track in trackList:
                if track['track'] == None:
                    print 'Track not available'
                    break
                if track['track']['id'] == None:
                    print 'Track not available'
                    break
                trackId = track['track']['id']
                if trackId not in seenTracks[category]:
                    seenTracks[category].add(trackId)
                    aa = spotify.audio_analysis(trackId)

                    if aa == None:
                        print 'Could not get Track'
                        break
                    track = spotify.track(trackId)
                    print(category + ' - ' + track['name'].encode("utf-8"))

                    # C, C#, D, D#, E, F, F#, G, G#, A, A#, B
                    # Chorus is usually around 25% of the songs duration
                    # Let's determine this time, and give a 5% leniency for segment timing.
                    # Cap the chorus at 25 seconds.
                    # Create datapoints that that has the starting note, four floats that describe increase or decrease in pitch, the timbre of the first note, and the key of the song.
                    # One hot encoding is used for naive bayes, which would not be good in this case.

                    melodyStartGuess = track['duration_ms'] / 4000
                    melodyThreshold = (track['duration_ms'] - (track['duration_ms'] * 0.95)) / 1000

                    closestSection = None
                    closestSectionStart = melodyStartGuess
                    closestSectionEnd = melodyStartGuess + 25
                    closestSectionDist = melodyThreshold
                    for section in aa['sections']:
                        sectionDist = abs(section['start'] - melodyStartGuess)
                        if sectionDist < closestSectionDist:
                            closestSection = section
                            closestSectionStart = section['start']
                            closestSectionDist = sectionDist
                            if section['duration'] < 25:
                                closestSectionEnd = section['start'] + section['duration']
                            else:
                                closestSectionEnd = section['start'] + 25

                    if closestSection == None:
                        for section in aa['sections']:
                            sectionEnd = section['start'] + section['duration']
                            if (sectionEnd) > closestSectionStart:
                                closestSection = section
                                break

                    for segmentNum in xrange(len(aa['segments']) - 4):
                        #print segmentNum
                        segment = aa['segments'][segmentNum]
                        dataString = ''
                        if segment['start'] > closestSectionStart:
                            if segment['start'] < closestSectionEnd:
                                noteCount = 0
                                noteNum = -1
                                NUM_NOTES = 12
                                for note in segment['pitches']:
                                    if note == 1.00:
                                        noteNum = noteCount
                                        dataString+=('1,')
                                    else:
                                        dataString+=('0,')
                                    noteCount = noteCount + 1
                                for nextSegNums in xrange(1, 5):
                                    nextSegment = aa['segments'][segmentNum + nextSegNums]
                                    noteCount = 0
                                    for note in nextSegment['pitches']:
                                        if note == 1.00:
                                            noteDiff = noteCount - noteNum
                                            if noteDiff > 6:
                                                noteDiff = noteDiff - 12
                                            elif noteDiff < -5:
                                                noteDiff = noteDiff + 12
                                            # Possible ranges are -5 - 6.
                                            dataString += (str(noteDiff) + ',')
                                            noteNum = noteCount
                                            break
                                        noteCount = noteCount + 1
                                for timNum in xrange(3):
                                    dataString += (str(segment['timbre'][timNum]) + ',')
                                dataString += '0,' * closestSection['key']
                                dataString += '1'
                                dataString += ',0' * (11 - closestSection['key'])
                                dataString += '\n'
                                dataFile.write(dataString)
                                labelFile.write(category + '\n')
                            else:
                                break
                else:
                    print('Duplicate song')
