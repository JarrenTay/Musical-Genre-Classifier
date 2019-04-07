# Given the audio analysis of a song, the start and end time to analyze, and its section,
# generate a list of data points

# Creates a data point with 31 dimensions:
# Starting note (one-hot encoded)       (12 dimensions)
# 4 Progressive changes in note pitches (4 dimensions)
# First three vectors of timbre         (3 dimensions)
# Key of song (one-hot encoded)         (12 dimensions)
def genData1(aa, csStart, csEnd, cs):
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
                dataList.append(data)
            else:
                break
    return dataList
