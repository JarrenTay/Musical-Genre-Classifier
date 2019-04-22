from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
from sklearn.externals.six import StringIO
from sklearn import tree
import sys
import os
import numpy as np
import graphviz
import pydot
from joblib import dump
import genDataPoints

dataPointVersion = 1
if len(sys.argv) > 1:
    dataPointVersion = int(sys.argv[1])

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

with open('data/musicPoints' + str(dataPointVersion) + '.data', 'r') as dataFile:
    with open('data/musicPoints' + str(dataPointVersion) + '.labels', 'r') as labelFile:
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

    clf = tree.DecisionTreeClassifier(max_depth = 7)
    clf = clf.fit(np.array(dataTrain), np.array(labelTrain))
    score = clf.score(np.array(dataTest), np.array(labelTest))
    if score > bestClfScore:
        bestClfScore = score
        bestClf = clf

dataLabels = genDataPoints.genLabels(dataPointVersion)
print 'Decision Tree Score: ' + '{:.2f}'.format(score.item() * 100)
dot_data = StringIO()
tree.export_graphviz(bestClf, out_file = dot_data, feature_names = dataLabels.featureNames, class_names = dataLabels.classNames)
graph = pydot.graph_from_dot_data(dot_data.getvalue())
graph[0].write_pdf('data/musicPointsTree' + str(dataPointVersion) + '.pdf')

labelDict2 = dict()
for key, val in labelDict.iteritems():
    if type(key) == int:
        labelDict2[key] = val

dump((bestClf, labelDict2), 'data/musicPoints' + str(dataPointVersion) + '.tree')

