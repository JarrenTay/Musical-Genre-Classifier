import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import random

XIndex = 16
YIndex = 17

cmap = matplotlib.cm.get_cmap('viridis')
genres2 = ['Pop / K-pop / Kids', 'Hip-Hop / Soul / R&B', 'Country', 'Latin', 'EDM', 'Rock', 'Indie', 'Folk & Acoustic', 'Classical', 'Jazz', 'Christian', 'Arab', 'Desi', 'Afro', 'Metal', 'Reggae', 'Blues', 'Punk', 'Funk']
genres = ['Pop', 'K-pop', 'Kids', 'Hip-Hop', 'Soul-R&B', 'Country', 'Latin', 'EDM', 'Rock', 'Indie', 'Folk & Acoustic', 'Classical', 'Jazz', 'Christian', 'Arab', 'Desi', 'Afro', 'Metal', 'Reggae', 'Blues', 'Punk', 'Funk']

fig = plt.figure()
ax1 = fig.add_subplot(111)
#rgba = cmap(0.5)
#print(rgba)

xList = list()
yList = list()

for _ in xrange(len(genres)):
    xList.append(list())
    yList.append(list())

with open('data/musicPoints.data', 'r') as data:
    with open('data/musicPoints.labels', 'r') as labels:
        for dataLine in data:
            #if random.random() < 0.1:
            dataLabel = labels.readline()[:-1]
            dataList = dataLine.split(',')
            xList[genres.index(dataLabel)].append(float(dataList[XIndex]))
            yList[genres.index(dataLabel)].append(float(dataList[YIndex]))
            
for dataLabel in genres:
    genreFloat = genres.index(dataLabel) / float(len(genres) - 1)
    col = cmap(genreFloat)
    ax1.scatter(xList[genres.index(dataLabel)], yList[genres.index(dataLabel)], s = 1, c = col, label = dataLabel)

plt.legend(loc='upper left')
plt.draw()
plt.pause(1000)
print 'hi'