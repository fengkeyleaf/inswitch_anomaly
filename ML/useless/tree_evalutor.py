from sklearn.tree import DecisionTreeClassifier
import argparse

"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# Read tree from a txt file.

# https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.predict
# https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.predict
# Evaluate using predict() or score()

def evaluate( f:str ) -> None:
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser( description = "Tree Evaluation" )
    parser.add_argument( "-t", "--tree", help = "", type = str, required = True )
    evaluate( parser.parse_args().tree )
