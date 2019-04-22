import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import random
#import Image

XIndex = 0
YIndex = 1
xLabel = ''
yLabel = 'Modality'
xLimL = -6
xLimR = 7
yLimB = -6
yLimT = 7

cmap = matplotlib.cm.get_cmap('viridis')
genres = ['Pop / K-pop / Kids', 'Hip-Hop / Soul / R&B', 'Country', 'Latin', 'EDM', 'Rock', 'Indie', 'Folk & Acoustic', 'Classical', 'Jazz', 'Christian', 'Arab', 'Desi', 'Afro', 'Metal', 'Reggae', 'Blues', 'Punk', 'Funk']
genres2 = ['Pop', 'K-pop', 'Kids', 'Hip-Hop', 'Soul-R&B', 'Country', 'Latin', 'EDM', 'Rock', 'Indie', 'Folk & Acoustic', 'Classical', 'Jazz', 'Christian', 'Arab', 'Desi', 'Afro', 'Metal', 'Reggae', 'Blues', 'Punk', 'Funk']

fig = plt.figure()
ax1 = fig.add_subplot(111)
#rgba = cmap(0.5)
#print(rgba)

xList = list()
yList = list()

for _ in xrange(len(genres)):
    xList.append(list())
    yList.append(list())

with open('data/musicPoints3.data', 'r') as data:
    with open('data/musicPoints3.labels', 'r') as labels:
        for dataLine in data:
            #if random.random() < 0.1:
            dataLabel = labels.readline()[:-1]
            dataList = dataLine.split(',')
            xList[genres.index(dataLabel)].append(float(dataList[XIndex]))
            yList[genres.index(dataLabel)].append(float(0))

for dataLabel in genres:
    genreFloat = genres.index(dataLabel) / float(len(genres) - 1)
    col = cmap(genreFloat)
    #ax1.scatter(xList[genres.index(dataLabel)], yList[genres.index(dataLabel)], s = 1, label = dataLabel)
    #zList = list()
    #for i in xrange(len(xList[genres.index(dataLabel)])):
    #    zList.append((xList[genres.index(dataLabel)],yList[genres.index(dataLabel)]))
    aList = list()
    for _ in xrange(3):
        newList = [0] * 1
        aList.append(np.array(newList))


    for i in xrange(len(xList[genres.index(dataLabel)])):
        x = int(xList[genres.index(dataLabel)][i])
        y = int(yList[genres.index(dataLabel)][i])
        aList[x][y] = aList[x][y] + 1
    npList = np.array(aList)

    plt.imshow(npList, cmap = 'hot', interpolation='nearest')
    plt.title(dataLabel)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    #ax1.set_xlim(xLimL, xLimR)
    #ax1.set_ylim(yLimB, yLimT)
    fileName = dataLabel
    fileName = fileName.replace('/', '-')
    plt.savefig('plots/' + fileName + '.png')
    ax1.cla()
    plt.clf()
    #plt.show()

plt.legend(loc='upper left')
#plt.draw()
#plt.pause(1000)
print 'hi'
