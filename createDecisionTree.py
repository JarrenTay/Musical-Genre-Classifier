from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn import tree
import sys
import os
import numpy as np
import graphviz
from joblib import dump


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

kf = KFold(n_splits = 5, shuffle = True)
bestClf = None
bestClfScore = 0
for trainIndex, testIndex in kf.split(npData):
    dataTrain, dataTest = npData[trainIndex], npData[testIndex]
    labelTrain, labelTest = npLabels[trainIndex], npLabels[testIndex]

    clf = tree.DecisionTreeClassifier(max_depth = None)
    #cross_val_score(clf, npData, npLabels, cv = 10)
    clf = clf.fit(np.array(dataTrain), np.array(labelTrain))
    score = clf.score(np.array(dataTest), np.array(labelTest))
    #print score
    if score > bestClfScore:
        bestClfScore = score
        bestClf = clf

labelDict2 = dict()
for key, val in labelDict.iteritems():
    if type(key) == int:
        labelDict2[key] = val

#dump(labelDict2, 'data/musicPoints.labelDict')
dump((bestClf, labelDict2), 'data/musicPoints.tree')

