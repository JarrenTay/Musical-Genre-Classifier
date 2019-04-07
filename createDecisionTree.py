from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn import tree
import sys
import os
import numpy as np
import graphviz
from joblib import dump


# TwoWayDict - credit to Sasha Chedygov (Stack Overflow)
# ------------------------------------------------------
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
# ------------------------------------------------------

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

kf = KFold(n_splits = 5, shuffle = True)
bestClf = None
bestClfScore = 0
for trainIndex, testIndex in kf.split(npData):
    dataTrain, dataTest = npData[trainIndex], npData[testIndex]
    labelTrain, labelTest = npLabels[trainIndex], npLabels[testIndex]

    clf = tree.DecisionTreeClassifier(max_depth = None)
    clf = clf.fit(np.array(dataTrain), np.array(labelTrain))
    score = clf.score(np.array(dataTest), np.array(labelTest))
    if score > bestClfScore:
        bestClfScore = score
        bestClf = clf

labelDict2 = dict()
for key, val in labelDict.iteritems():
    if type(key) == int:
        labelDict2[key] = val

dump((bestClf, labelDict2), 'data/musicPoints.tree')

