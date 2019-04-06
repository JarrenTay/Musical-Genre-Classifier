from sklearn.datasets import load_iris
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
import sys
import os
import numpy as np

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
            dataFloatArray = np.array(dataFloatList)
            dataList.append(dataFloatArray)
            
            labelStr = labelFile.readline()
            if labelStr not in labelDict:
                numLabels = numLabels + 1
                labelDict[labelStr] = numLabels
            
            labelList.append(labelDict[labelStr])

npData = np.array(dataList)
npLabels = np.array(labelList)

clf = DecisionTreeClassifier(random_state = 0)
#cross_val_score(clf, npData, npLabels, cv = 10)
fit(npData, npLabels)
print decision_path