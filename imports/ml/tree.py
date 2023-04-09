# -*- coding: utf-8 -*-
"""
file that takes training data as input and produces a tree as output

sean bergen
"""

import sys
from csv import reader
import numpy as np
from typing import (
    List
)

from sklearn import tree
from sklearn.tree import (
    DecisionTreeClassifier
)

"""
load data in from csv file
"""
file = open(sys.argv[1])
reader = reader(file)

"""
get rid of headers
"""
headers = next(reader)

data = []
labels = []
"""
formatting from the csv is kinda weird so it is explained here:
    each line looks something like:
        "[sketch]",label
    so, we need to unpack the sketch back into a list from a string
    and then also make sure each part of the sketch is read in as an integer
"""
for line in reader:
    tmp1 = line[0].strip('][').split(',')
    tmp2 = []
    for item in tmp1:
        tmp2.append(int(item))
    labels.append(int(line[1]))
    
    data.append(tmp2)

"""
pass data into tree

the data comprises everything except for the last index of the data array

the last index of data is actually the label
"""

def get_lineage(tree, feature_names, file):
    srcCount = []
    dstCount = []
    srcTLS = []
    dstTLS = []
    left = tree.tree_.children_left
    right = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features = [feature_names[i] for i in tree.tree_.feature]
    value = tree.tree_.value
    le = '<='
    g = '>'
    # get ids of child nodes
    idx = np.argwhere(left == -1)[:, 0]

    # traverse the tree and get the node information
    def recurse(left, right, child, lineage=None):
        if lineage is None:
            lineage = [child]
        if child in left:
            parent = np.where(left == child)[0].item()
            split = 'l'
        else:
            parent = np.where(right == child)[0].item()
            split = 'r'
        
        lineage.append((parent, split, threshold[parent], features[parent]))
        if parent == 0:
            lineage.reverse()
            return lineage
        else:
            return recurse(left, right, parent, lineage)
    
    for j, child in enumerate(idx):
        clause = ' when '
        for node in recurse(left, right, child):
            if len(str(node)) < 3:
                continue
            i = node

            if i[1] == 'l':
                sign = le
            else:
                sign = g
            clause = clause + i[3] + sign + str(i[2]) + ' and '
    
    # write the node information into text file
        a = list(value[node][0])
        ind = a.index(max(a))
        clause = clause[:-4] + ' then ' + str(ind)
        file.write(clause)
        file.write(";\n")


class Evaluator:
    def __init__( self, X: List, y: List, t: DecisionTreeClassifier ) -> None:
        """
        :param X: array-like of shape (n_samples, n_features)
        :param y: array-like of shape (n_samples,) or (n_samples, n_outputs)
        :param t: decisoin tree
        """
        self.X = X
        self.t = t
        self.y = y

    # python3 ./ML/tree.py /home/p4/tutorials/exercises/inswitch_anomaly-data_labeling/test/test_data/sketch.csv /home/p4/tutorials/exercises/inswitch_anomaly-data_labeling/test/tree.txt
    def evaluate( self ) -> None:
        # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.predict
        # print( self.t.predict( self.X ) )
        # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.score
        print( "Accuracy of this tree: %.2f" % ( self.t.score( self.X, self.y ) * 100 ) )


decision_tree = tree.DecisionTreeClassifier()
# https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.fit
decision_tree = decision_tree.fit(data, labels)

# Evaluate the tree
Evaluator( data, labels, decision_tree ).evaluate()

feature_names = ["srcCount", "dstCount", "srcTLS", "dstTLS"]

threshold = decision_tree.tree_.threshold
features = [feature_names[i] for i in decision_tree.tree_.feature]

srcCount = []
dstCount = []
srcTLS = []
dstTLS = []

for i, fe in enumerate(features):
    if fe == 'srcCount':
        srcCount.append(threshold[i])
    elif fe =='dstCount':
        dstCount.append(threshold[i])
    elif fe == 'srcTLS':
        srcTLS.append(threshold[i])
    else:
        dstTLS.append(threshold[i])

srcCount = [int(i) for i in srcCount]
dstCount = [int(i) for i in dstCount]
srcTLS = [int(i) for i in srcTLS]
dstTLS = [int(i) for i in dstTLS]

srcCount.sort()
dstCount.sort()
srcTLS.sort()
dstTLS.sort()

output = open(sys.argv[2], "w+")
output.write("srcCount = ")
output.write(str(srcCount))
output.write(";\n")
output.write("dstCount = ")
output.write(str(dstCount))
output.write(";\n")
output.write("srcTLS = ")
output.write(str(srcTLS))
output.write(";\n")
output.write("dstTLS = ")
output.write(str(dstTLS))
output.write(";\n")
get_lineage(decision_tree, feature_names, output)
output.close()

"""
clf = tree.DecisionTreeClassifier()

clf.fit(data,labels)
tree.plot_tree(clf)
plt.savefig(sys.argv[2],format="png",dpi=1200)
plt.show()
"""