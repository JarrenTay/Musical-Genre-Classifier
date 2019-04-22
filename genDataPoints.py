import numpy as np

class DataLabel:
    
    def __init__(self, featureNames, classNames):
        self.featureNames = featureNames
        self.classNames = classNames

# Given the audio analysis of a song, the start and end time to analyze, and its section,
# generate a list of data points

# Creates a data point with 31 dimensions:
# Starting note (one-hot encoded)       (12 dimensions)
# 4 Progressive changes in note pitches (4 dimensions)
# First three vectors of timbre         (3 dimensions)
# Key of song (one-hot encoded)         (12 dimensions)
def _genData1(aa, csStart, csEnd, cs):
    dataList = list()
    
    for segmentNum in xrange(len(aa['segments']) - 4):
        segment = aa['segments'][segmentNum]
        data = list()
        if segment['start'] > csStart:
            if segment['start'] < csEnd:
                noteCount = 0
                noteNum = -1
                NUM_NOTES = 12
                for note in segment['pitches']:
                    if note == 1.00:
                        noteNum = noteCount
                        data.append(1)
                    else:
                        data.append(0)
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
                            data.append(noteDiff)
                            noteNum = noteCount
                            break
                        noteCount = noteCount + 1
                for timNum in xrange(3):
                    data.append(segment['timbre'][timNum])
                for _ in xrange(cs['key']):
                    data.append(0)
                data.append(1)
                for _ in xrange(11 - cs['key']):
                    data.append(0)
                if len(data) == 31:
                    dataList.append(data)
            else:
                break
    return dataList

def _genLabel1():
    featureNames = ['Note: C','Note: C#','Note: D','Note: D#','Note: E','Note: F','Note: F#','Note: G','Note: G#','Note: A','Note: A#','Note: B','Progression 0','Progression 1','Progression 2','Progression 3','Timbre 0','Timbre 1','Timbre 2','Key: C','Key: C#','Key: D','Key: D#','Key: E','Key: F','Key: F#','Key: G','Key: G#','Key: A','Key: A#','Key: B']
    classNames = ['Pop / K-pop / Kids','Hip-Hop / Soul / R&B','Country','Latin','EDM','Rock','Indie','Folk & Acoustic','Classical','Jazz','Christian','Arab','Desi','Afro','Metal','Reggae','Blues','Punk','Funk']
    dataLabel = DataLabel(np.array(featureNames), np.array(classNames))
    return dataLabel


# Creates a data point with 28 dimensions:
# 4 Progressive changes in note pitches (4 dimensions)
# Twelve vectors of timbre              (12 dimensions)
# Key of song (one-hot encoded)         (12 dimensions)
def _genData2(aa, csStart, csEnd, cs):
    dataList = list()
    
    for segmentNum in xrange(len(aa['segments']) - 4):
        segment = aa['segments'][segmentNum]
        data = list()
        if segment['start'] > csStart:
            if segment['start'] < csEnd:
                noteCount = 0
                noteNum = -1
                NUM_NOTES = 12
                for note in segment['pitches']:
                    if note == 1.00:
                        noteNum = noteCount
                        break
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
                            data.append(noteDiff)
                            noteNum = noteCount
                            break
                        noteCount = noteCount + 1
                data.extend(segment['timbre'])
                for _ in xrange(cs['key']):
                    data.append(0)
                data.append(1)
                for _ in xrange(11 - cs['key']):
                    data.append(0)
                if len(data) == 28:
                    dataList.append(data)
            else:
                break
    return dataList

def _genLabel2():
    featureNames = ['Progression 0','Progression 1','Progression 2','Progression 3','Timbre 0','Timbre 1','Timbre 2','Timbre 3','Timbre 4','Timbre 5','Timbre 6','Timbre 7','Timbre 8','Timbre 9','Timbre 10','Timbre 11','Key: C','Key: C#','Key: D','Key: D#','Key: E','Key: F','Key: F#','Key: G','Key: G#','Key: A','Key: A#','Key: B']
    classNames = ['Pop / K-pop / Kids','Hip-Hop / Soul / R&B','Country','Latin','EDM','Rock','Indie','Folk & Acoustic','Classical','Jazz','Christian','Arab','Desi','Afro','Metal','Reggae','Blues','Punk','Funk']
    dataLabel = DataLabel(np.array(featureNames), np.array(classNames))
    return dataLabel

# Creates a data point with 21 dimensions:
# Modality                              (1 dimension)
# Eight vectors of timbre               (8 dimensions)
# Key of song (one-hot encoded)         (12 dimensions)
def _genData3(aa, csStart, csEnd, cs):
    dataList = list()
    
    for segmentNum in xrange(len(aa['segments']) - 4):
        segment = aa['segments'][segmentNum]
        data = list()
        if segment['start'] > csStart:
            if segment['start'] < csEnd:
                data.append(cs['mode'])
                data.extend(segment['timbre'][0:8])
                for _ in xrange(cs['key']):
                    data.append(0)
                data.append(1)
                for _ in xrange(11 - cs['key']):
                    data.append(0)
                if len(data) == 21:
                    dataList.append(data)
            else:
                break
    return dataList

def _genLabel3():
    featureNames = ['Mode','Timbre 0','Timbre 1','Timbre 2','Timbre 3','Timbre 4','Timbre 5','Timbre 6','Timbre 7','Key: C','Key: C#','Key: D','Key: D#','Key: E','Key: F','Key: F#','Key: G','Key: G#','Key: A','Key: A#','Key: B']
    classNames = ['Pop / K-pop / Kids','Hip-Hop / Soul / R&B','Country','Latin','EDM','Rock','Indie','Folk & Acoustic','Classical','Jazz','Christian','Arab','Desi','Afro','Metal','Reggae','Blues','Punk','Funk']
    dataLabel = DataLabel(np.array(featureNames), np.array(classNames))
    return dataLabel

gdVersions = {1: _genData1, 2: _genData2, 3: _genData3}

glVersions = {1: _genLabel1, 2: _genLabel2, 3: _genLabel3}

# Selector for which function genData function to use
def genData(aa, csStart, csEnd, cs, gdVer):
    return gdVersions.get(gdVer)(aa, csStart, csEnd, cs)

def genLabels(glVer):
    return glVersions.get(glVer)()

