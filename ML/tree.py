# -*- coding: utf-8 -*-
"""
file that takes training data as input and produces a tree as output

sean bergen
"""

import sys
from csv import reader
import random as rd
import numpy as np
from matplotlib import pyplot as plt

from sklearn import tree

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

decision_tree = tree.DecisionTreeClassifier()
decision_tree = decision_tree.fit(data, labels)

r = tree.export_text(decision_tree, feature_names=['srcCount', 'srcTLS', 'dstCount', 'dstTLS'])

tree.plot_tree(decision_tree)
plt.show()

print(r)

"""
clf = tree.DecisionTreeClassifier()

clf.fit(data,labels)
tree.plot_tree(clf)
plt.savefig(sys.argv[2],format="png",dpi=1200)
plt.show()
"""