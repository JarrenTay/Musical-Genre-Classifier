from sklearn import tree
import sys
import spotipy
import spotipy.util as util
import webbrowser
import requests
import json
import base64
import time
import numpy as np
from joblib import load
import genDataPoints

dataPointVersion = 1
trackUrl = sys.argv[1]
if len(sys.argv) > 2:
    dataPointVersion = int(sys.argv[1])
    trackUrl = sys.argv[2]

bestClf, labelDict = load('data/musicPoints' + str(dataPointVersion) + '.tree')

info = open('ssh', 'r')
username = info.readline()[:-1]
clientId = info.readline()[:-1]
clientSecret = info.readline()[:-1]
redirect = info.readline()[:-1]

scope = 'user-library-read app-remote-control streaming'

token = util.prompt_for_user_token(username, scope, clientId, clientSecret, redirect)

spotify = spotipy.Spotify(auth=token)

trackUrlList = trackUrl.split(':')

if len(trackUrlList) == 3: # Track
    tracks = [trackUrlList[2]]
else:
    tracks = [song['track']['id'] for song in spotify.user_playlist_tracks(trackUrlList[2], trackUrlList[4])['items']]

songNum = 0
with open('data/musicPoints' + str(dataPointVersion) + '.class', 'a+') as classFile:
    outString = ''
    for trackId in tracks:
        songNum = songNum + 1
        aa = spotify.audio_analysis(trackId)
        
        if aa == None:
            print 'Could not get Track'
            sys.exit()
        track = spotify.track(trackId)
        
        artistString = ''
        for artist in track['artists']:
            artistString = artistString + artist['name'].replace(',', '').encode("utf-8") + ' + '
        
        outString += track['name'].replace(',', '').encode('utf-8') + ','
        print track['name'].encode('utf-8') + ' by ' + artistString[:-3]
        outString += artistString[:-3] + ','
        
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
        
        dataList = genDataPoints.genData(aa, closestSectionStart, closestSectionEnd, closestSection, dataPointVersion)
        if len(dataList) > 0:
            dataFloatList = list()
            for data in dataList:
                dataFloatList.append([float(dataDim) for dataDim in data])
            
            npData = np.array(dataFloatList)
            npPredictLabels = bestClf.predict(npData)
            
            predictLabels = npPredictLabels.tolist()
            
            classDict = dict()
            
            for label in predictLabels:
                if labelDict[label] not in classDict:
                    classDict[labelDict[label]] = 0
                classDict[labelDict[label]] = classDict[labelDict[label]] + 1
            
            classTot = float(len(dataList)) / 100
            topX = min(5, len(classDict))
            
            topList = list()
            for rank in xrange(topX):
                maxKey = ''
                maxVal = -1
                for key, val in classDict.iteritems():
                    if val > maxVal:
                        maxKey = key
                        maxVal = val
                topList.append(maxKey)
                del classDict[maxKey]
        
            genreOut = ''
            for genre in topList:
                genreOut += genre + ','
    
            outString += genreOut[:-1] + '\n'
            print genreOut[:-1] + '\n'
        else:
            outString += "Could not generate data and classify\n"

    classFile.write(outString)
