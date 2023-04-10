# -*- coding: utf-8 -*-

"""
file: file that takes training data as input and produces a tree as output
description: file to do sketch building and write results to a csv file
language: python3 3.11.3
author: @sean bergen,
        @Riley,
        @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

import csv
import math
import sys
from collections import OrderedDict

import numpy as np
from typing import (
    List,
    Dict
)
from argparse import (
    ArgumentParser
)

from sklearn import tree
from sklearn.tree import (
    DecisionTreeClassifier
)

sys.path.append( "../com/fengkeyleaf/utils/" )
import my_collections


# https://github.com/cucl-srg/IIsy/blob/master/iisy_sw/framework/Machinelearning.py
def get_lineage( tree, feature_names, file ):
    """
    pass data into tree

    the data comprises everything except for the last index of the data array

    the last index of data is actually the label
    @param tree:
    @param feature_names:
    @param file:
    @return:
    """
    srcCount = [ ]
    dstCount = [ ]
    srcTLS = [ ]
    dstTLS = [ ]
    left = tree.tree_.children_left
    right = tree.tree_.children_right
    threshold = tree.tree_.threshold
    features = [ feature_names[ i ] for i in tree.tree_.feature ]
    value = tree.tree_.value
    le = '<='
    g = '>'
    # get ids of child nodes
    idx = np.argwhere( left == -1 )[ :, 0 ]

    # traverse the tree and get the node information
    def recurse( left, right, child, lineage = None ):
        if lineage is None:
            lineage = [ child ]
        if child in left:
            # https://numpy.org/doc/stable/reference/generated/numpy.where.
            # https://www.cnblogs.com/massquantity/p/8908859.html
            # print( np.where( left == child ) )
            # print( type( np.where( left == child )[ 0 ] ) )
            # print( np.where( left == child )[ 0 ] )
            # print( np.where( left == child )[ 0 ].item() )
            # https://numpy.org/doc/stable/reference/generated/numpy.ndarray.item.html
            parent = np.where( left == child )[ 0 ].item()
            split = 'l'
        else:
            parent = np.where( right == child )[ 0 ].item()
            split = 'r'

        lineage.append( ( parent, split, threshold[ parent ], features[ parent ] ) )
        if parent == 0:
            lineage.reverse()
            return lineage
        else:
            return recurse( left, right, parent, lineage )

    for j, child in enumerate( idx ):
        clause = ' when '
        # print( recurse( left, right, child ) )
        for node in recurse( left, right, child ):
            # print( "node: " + str( node ) + " " + str( len( str( node ) ) ) )
            # https://www.geeksforgeeks.org/type-isinstance-python/
            # https://www.stechies.com/check-data-type-python/
            # print( type( node ) )
            if isinstance( node, np.int64 ):
                continue
            i = node

            # print( i )
            if i[ 1 ] == 'l':
                sign = le
            else:
                sign = g
            clause = clause + i[ 3 ] + sign + str( i[ 2 ] ) + ' and '

        # write the node information into text file
        a = list( value[ node ][ 0 ] )
        ind = a.index( max( a ) )
        clause = clause[ :-4 ] + ' then ' + str( ind )
        file.write( clause )
        file.write( ";\n" )


class Tree:
    def __init__( self, f: str, o: str ) -> None:
        # load data in from csv file
        file = open( f )
        self.reader = csv.reader( file )
        # get rid of headers
        next( self.reader )
        self.data = [ ]
        self.labels = [ ]
        self.reformatting()
        self.get_tree( o )

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
            print( "Accuracy of this tree: %.2f%%" % (self.t.score( self.X, self.y ) * 100) )

    def reformatting( self ):
        """
        formatting from the csv is kinda weird so it is explained here:
            each line looks something like:
                "[sketch]",label
            so, we need to unpack the sketch back into a list from a string
            and then also make sure each part of the sketch is read in as an integer
        """
        for line in self.reader:
            tmp1 = line[ 0 ].strip( '][' ).split( ',' )
            tmp2 = []
            for item in tmp1:
                tmp2.append( int( item ) )

            self.labels.append( int( line[ 1 ] ) )
            self.data.append( tmp2 )

    def get_tree( self, o: str ):
        decision_tree = tree.DecisionTreeClassifier()
        # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.fit
        decision_tree = decision_tree.fit( self.data, self.labels )

        # Evaluate the tree
        Tree.Evaluator( self.data, self.labels, decision_tree ).evaluate()

        feature_names = [ "srcCount", "srcTLS", "dstCount", "dstTLS" ]

        threshold = decision_tree.tree_.threshold
        features = [ feature_names[ i ] for i in decision_tree.tree_.feature ]

        F: Dict[ str: List ] = { f: [] for f in feature_names }
        # srcCount = [ ]
        # dstCount = [ ]
        # srcTLS = [ ]
        # dstTLS = [ ]

        # https://www.geeksforgeeks.org/enumerate-in-python/
        for i, fe in enumerate( features ):
            F[ fe ].append( threshold[ i ] )
            # if fe == 'srcCount':
            #     srcCount.append( threshold[ i ] )
            # elif fe == 'dstCount':
            #     dstCount.append( threshold[ i ] )
            # elif fe == 'srcTLS':
            #     srcTLS.append( threshold[ i ] )
            # else:
            #     assert fe == "dstTLS"
            #     dstTLS.append( threshold[ i ] )

        for k, v in F.items():
            v = [ int( i ) for i in v if int( i ) > 0 ]
            # https://www.geeksforgeeks.org/python-ways-to-remove-duplicates-from-list/
            v = list( OrderedDict.fromkeys( v ) )
            v.sort()
            F[ k ] = v

            if v[ 0 ] > 0:
                v.insert( 0, int( 0 ) )

            assert v[ -1 ] < int( math.pow( 2, 31 ) )
            v.append( int( math.pow( 2, 31 ) ) )

            assert my_collections.is_monotonic( v )

        # srcCount = [ int( i ) for i in srcCount if int( i ) > 0 ]
        # dstCount = [ int( i ) for i in dstCount if int( i ) > 0 ]
        # srcTLS = [ int( i ) for i in srcTLS if int( i ) > 0 ]
        # dstTLS = [ int( i ) for i in dstTLS if int( i ) > 0 ]

        # srcCount.sort()
        # dstCount.sort()
        # srcTLS.sort()
        # dstTLS.sort()

        # Write to file
        # srcCount
        # srcTLS
        # dstCount
        # dstTLS
        output = open( o, "w+" )
        # https://www.w3schools.com/python/python_dictionaries_loop.asp
        for k, v in F.items():
            output.write( k + " = " )
            output.write( str( v ) )
            output.write( ";\n" )

        # output.write( "srcCount = " )
        # output.write( str( srcCount ) )
        # output.write( ";\n" )
        # output.write( "srcTLS = " )
        # output.write( str( srcTLS ) )
        # output.write( ";\n" )
        # output.write( "dstCount = " )
        # output.write( str( dstCount ) )
        # output.write( ";\n" )
        # output.write( "dstTLS = " )
        # output.write( str( dstTLS ) )
        # output.write( ";\n" )

        get_lineage( decision_tree, feature_names, output )
        output.close()


if __name__ == '__main__':
    parser:ArgumentParser = ArgumentParser()
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    parser.add_argument( "-s", "--sketch", type = str, help = "Path to sketch csv file", required = True )
    parser.add_argument( "-dt", "--decisionTree", type = str, help = "Path to decision tree txt file", required = True )

    args = parser.parse_args()
    Tree( args.sketch, args.decisionTree )