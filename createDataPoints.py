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

playlistListFile = open('playlistList.txt', 'r')

playlistListRaw = playlistListFile.read()

playlistList = playlistListRaw.split('\n')
for playlistRaw in playlistList:    
    lineList = playlistRaw.split(',')
    category = lineList[0]
    infoList = lineList[1].split(':')
    userId = infoList[2]
    playlistId = infoList[4]
    
    playlist = spotify.user_playlist_tracks(userId, playlistId)
    numTracks = playlist['total']
    trackList = playlist['items']
    
    with open('data/' + category + '.data', 'a+') as dataFile:
        for track in trackList:
            trackId = track['track']['id']
            print trackId
            
            aa = spotify.audio_analysis(trackId)
            track = spotify.track(trackId)
            print track['name']
            
            # C, C#, D, D#, E, F, F#, G, G#, A, A#, B
            # Chorus is usually around 25% of the songs duration
            # Let's determine this time, and give a 5% leniency for segment timing.
            # Cap the chorus at 25 seconds.
            # Create datapoints that that has a starting note (one-hot encoded), four ints that describe increase or decrease in pitch, the timbre of the first note, and the key of the song.
            
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
                                        noteDiff = -(noteDiff - 6)
                                    elif noteDiff < -6:
                                        noteDiff = -(noteDiff + 6)
                                    dataString+=(str(noteDiff) + ',')
                                    noteNum = noteCount
                                    break
                                noteCount = noteCount + 1
                        for timNum in xrange(3):
                            dataString+=(str(segment['timbre'][timNum]) + ',')
                        dataString+=(str(closestSection['key']) + '\n')
                    else:
                        break
                dataFile.write(dataString)

                



