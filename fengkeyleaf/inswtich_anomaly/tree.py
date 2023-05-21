# -*- coding: utf-8 -*-

import logging
import math
from argparse import (
    ArgumentParser
)
from collections import OrderedDict
from typing import (
    List,
    Dict,
    Tuple
)
import ast
import numpy as np
import pandas
import sklearn.tree
from sklearn import tree
from sklearn.tree import (
    DecisionTreeClassifier
)

"""
file: file that takes training data as input and produces a tree as output
description: file to do sketch building and write results to a csv file
language: python3 3.11.3
author: @sean bergen,
        @Riley,
        @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import (
    my_logging,
)
from fengkeyleaf.io import (
    my_writer,
    my_files
)
from fengkeyleaf.utils import my_collections
from fengkeyleaf.inswtich_anomaly import (
    sketch_write,
    csvparaser
)


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


# TODO: Use pandas
class Tree:
    """
    Train decision trees with sketch csv files.
    """
    FOLDER_NAME = "/trees/"
    SIGNATURE = "_tree.txt"

    def __init__( self, d: str, pd: str, D: List[ str ], ll: int = logging.INFO ) -> None:
        """

        @param d: Directory to pkt sketch csv files.
        @param pd: Directory to original pkt csv files.
        @param D: List of directories to the processed data sets to test trees.
        @param ll: logging level
        """
        self.l = my_logging.get_logger( ll )
        self.e = Tree.__Evaluator( self.l, D )

        self.d = d
        self.pd = pd

    def process( self, df: pandas.DataFrame, f: str ) -> None:
        data, labels = Tree.reformatting( df )
        # print( data )
        # print( labels )
        self.get_tree( f, data, labels )

    class __Evaluator:
        def __init__( self, l: logging.Logger, D: List[ str ] ) -> None:
            """
            :param X: array-like of shape (n_samples, n_features)
            :param y: array-like of shape (n_samples,) or (n_samples, n_outputs)
            :param t: decisoin tree
            """
            self.file_list: List[ List[ str ] ] = my_files.get_files_in_dirs( D )

            self.l = l

        # python3 ./ML/tree.py /home/p4/tutorials/exercises/inswitch_anomaly-data_labeling/test/test_data/sketch.csv /home/p4/tutorials/exercises/inswitch_anomaly-data_labeling/test/tree.txt
        def evaluate(
                self, t: DecisionTreeClassifier, tf: str,
                t_data: List[ List[ int ] ], t_labels: List[ int ]
        ) -> None:
            """

            @param t: The tree.
            @param tf: Tree file path.
            @param t_data: Tree's training data.
            @param t_labels: Tree's label data
            """
            if len( self.file_list ) <= 0:
                self.l.debug( "Accuracy of this tree: %.2f%%" % ( t.score( t_data, t_labels ) * 100 ) )
                return

            self.l.debug( "Accuracy of this tree: %.2f%%" % (t.score( t_data, t_labels ) * 100) )
            # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.predict
            # print( self.t.predict( self.X ) )
            # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.score
            self.l.debug( "Verifying the tree with the sketch file: %s" % my_writer.get_filename( tf ) )
            for F in self.file_list:
                for fp in F:
                    with open(
                            fp, encoding = my_files.UTF8,
                            errors = my_files.BACK_SLASH_REPLACE
                    ) as f:
                        assert my_writer.get_extension( fp ).lower() == my_files.CSV
                        data, labels = Tree.reformatting( pandas.read_csv( f ) )
                        self.l.debug( my_writer.get_filename( fp ) )
                        self.l.debug( "Accuracy: %.2f%%" % ( t.score( data, labels ) * 100 ) )

    @staticmethod
    def reformatting( df: pandas.DataFrame ) -> Tuple[ List[ List[ int ] ], List[ int ] ]:
        """
        formatting from the csv is kinda weird so it is explained here:
        each line looks something like:
            "[sketch]",label
        so, we need to unpack the sketch back into a list from a string
        and then also make sure each part of the sketch is read in as an integer
        """
        data: List[ List[ int ] ] = []
        labels: List[ int ] = []

        for ( i, _ ) in df.iterrows():
            # print( df.loc[ i, sketch_write.RANGE_STR ] )
            # tmp1: List[ str ] = df.loc[ i, sketch_write.RANGE_STR ].strip( '][' ).split( ',' )
            # tmp2: List[ int ] = []
            # for item in tmp1:
            #     tmp2.append( int( item ) )

            labels.append( df.loc[ i, csvparaser.LABEL_STR ] )
            assert labels[ -1 ] == sketch_write.GOOD_LABEL or labels[ -1 ] == sketch_write.BAD_LABEL
            l = df.loc[ i, sketch_write.RANGE_STR ]
            assert isinstance( l, str ) or isinstance( l, list )
            data.append( ast.literal_eval( l ) if isinstance( l, str ) else l )

        return ( data, labels )

    def get_tree( self, f: str, data, labels ):
        d: str = my_writer.get_dir( f ) + Tree.FOLDER_NAME
        my_writer.make_dir( d )
        f = d + my_writer.get_filename( f ) + Tree.SIGNATURE
        self.l.info( "tree: " + f )

        decision_tree = tree.DecisionTreeClassifier()
        # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.fit
        decision_tree = decision_tree.fit( data, labels )

        # Evaluate the tree
        self.e.evaluate( decision_tree, f, data, labels )

        # TODO: Configuration of features.
        feature_names = [ "srcCount", "srcTLS", "dstCount", "dstTLS" ]

        # tree_Tree instance
        threshold = decision_tree.tree_.threshold
        # print( threshold )
        # print( decision_tree.tree_.feature )
        features = [ feature_names[ i ] for i in decision_tree.tree_.feature ]
        # print( features )

        F: Dict[ str: List ] = { f: [] for f in feature_names }

        # https://scikit-learn.org/stable/auto_examples/tree/plot_unveil_tree_structure.html#sphx-glr-auto-examples-tree-plot-unveil-tree-structure-py
        # tree.plot_tree( decision_tree )
        # plt.show()
        # https://towardsdatascience.com/scikit-learn-decision-trees-explained-803f3812290d
        sklearn.tree.export_graphviz(
            decision_tree,
            out_file = "myTreeName.dot",
            filled = True,
            rounded = True
        )
        # https://www.geeksforgeeks.org/enumerate-in-python/
        for i, fe in enumerate( features ):
            F[ fe ].append( threshold[ i ] )

        # print( F )
        for k, v in F.items():
            v = [ int( i ) for i in v if int( i ) > 0 ]
            # https://www.geeksforgeeks.org/python-ways-to-remove-duplicates-from-list/
            v = list( OrderedDict.fromkeys( v ) )
            v.sort()
            F[ k ] = v

            if len( v ) <= 0:
                self.l.warning( "Warning! Empty Feature: " + f )
                continue

            assert len( v ) > 0, str( k ) + " | " + str( v )
            # TODO: simplify
            if v[ 0 ] > 0:
                v.insert( 0, int( 0 ) )

            assert v[ -1 ] < int( math.pow( 2, 31 ) )
            v.append( int( math.pow( 2, 31 ) ) )

            assert my_collections.is_monotonic( v )

        # Write to file
        # srcCount
        # srcTLS
        # dstCount
        # dstTLS
        output = open( f, "w+" )
        # https://www.w3schools.com/python/python_dictionaries_loop.asp
        for k, v in F.items():
            output.write( k + " = " )
            output.write( str( v ) )
            output.write( ";\n" )

        get_lineage( decision_tree, feature_names, output )
        output.close()


if __name__ == '__main__':
    parser:ArgumentParser = ArgumentParser()
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    # parser.add_argument( "-s", "--sketch", type = str, help = "Path to sketch csv file", required = True )
    # parser.add_argument( "-dt", "--decisionTree", type = str, help = "Path to decision tree txt file", required = True )

    args = parser.parse_args()
    # Tree( args.sketch, args.decisionTree )