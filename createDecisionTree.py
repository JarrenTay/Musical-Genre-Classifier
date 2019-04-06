from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn import tree
import sys
import os
import numpy as np
import graphviz
import spotipy
import spotipy.util as util
import webbrowser
import requests
import json
import base64
import time

# TwoWayDict - credit to Sasha Chedygov (Stack Overflow)
class TwoWayDict(dict):
    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        return dict.__len__(self) // 2

labelDict = TwoWayDict()
dataList = list()
labelList = list()

with open('data/musicPoints.data', 'r') as dataFile:
    with open('data/musicPoints.labels', 'r') as labelFile:
        numLabels = 0
        for dataLine in dataFile:
            dataListRaw = dataLine[:-1].split(',')
            dataFloatList = [float(data) for data in dataListRaw]
            #dataFloatArray = np.array(dataFloatList)
            dataList.append(dataFloatList)
            
            labelStr = labelFile.readline()[:-1]
            if labelStr not in labelDict:
                labelDict[labelStr] = numLabels
                numLabels = numLabels + 1
            
            labelList.append(labelDict[labelStr])

npData = np.array(dataList)
npLabels = np.array(labelList)

targetNamesList = list()
for labelId in xrange(numLabels):
    targetNamesList.append(labelDict[labelId])

targetNames = np.array(targetNamesList, dtype='|S10')

featureNames = ['startC', 'startC#', 'startD', 'startD#', 'startE', 'startF', 'startF#', 'startG', 'startG#', 'startA', 'startA#', 'startB', 'diff1', 'diff2', 'diff3', 'diff4', 'timb1', 'timb2', 'timb3', 'keyC', 'keyC#', 'keyD', 'keyD#', 'keyE', 'keyF', 'keyF#', 'keyG', 'keyG#', 'keyA', 'keyA#', 'keyB']
#print npData
#print npData.size, npLabels.size

#print labelDict

clf = tree.DecisionTreeClassifier(max_depth = None)
#cross_val_score(clf, npData, npLabels, cv = 10)
clf = clf.fit(npData, npLabels)


info = open('ssh', 'r')
username = info.readline()[:-1]
clientId = info.readline()[:-1]
clientSecret = info.readline()[:-1]
redirect = info.readline()[:-1]

scope = 'user-library-read app-remote-control streaming'

token = util.prompt_for_user_token(username, scope, clientId, clientSecret, redirect)

spotify = spotipy.Spotify(auth=token)

trackUrl = sys.argv[1]
trackUrlList = trackUrl.split(':')
trackId = trackUrlList[-1]

aa = spotify.audio_analysis(trackId)

if aa == None:
    print 'Could not get Track'
    sys.exit()
track = spotify.track(trackId)
print(track['name'].encode("utf-8"))
for artist in track['artists']:
    print artist['name'].encode("utf-8")



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

dataList = list()

for segmentNum in xrange(len(aa['segments']) - 4):
    #print segmentNum
    segment = aa['segments'][segmentNum]
    dataFloat = list()
    if segment['start'] > closestSectionStart:
        if segment['start'] < closestSectionEnd:
            noteCount = 0
            noteNum = -1
            NUM_NOTES = 12
            for note in segment['pitches']:
                if note == 1.00:
                    noteNum = noteCount
                    dataFloat.append(float(1))
                else:
                    dataFloat.append(float(0))
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
                        dataFloat.append(float(noteDiff))
                        noteNum = noteCount
                        break
                    noteCount = noteCount + 1
            for timNum in xrange(3):
                dataFloat.append(float(segment['timbre'][timNum]))
            for _ in xrange(closestSection['key']):
                dataFloat.append(float(0))
            dataFloat.append(float(1))
            for _ in xrange(11 - closestSection['key']):
                dataFloat.append(float(0))
            npDataFloat = np.array(dataFloat)
            dataList.append(dataFloat)
        else:
            break

#print dataList

npData = np.array(dataList)
npPredictLabels = clf.predict(npData)

predictLabels = npPredictLabels.tolist()

classDict = dict()

for label in predictLabels:
    if labelDict[label] not in classDict:
        classDict[labelDict[label]] = 0
    classDict[labelDict[label]] = classDict[labelDict[label]] + 1

#print classDict

for _ in xrange(len(classDict)):
    maxKey = ''
    maxVal = -1
    for key, val in classDict.iteritems():
        if val > maxVal:
            maxKey = key
            maxVal = val
    print maxKey, maxVal
    del classDict[maxKey]


