# -*- coding: utf-8 -*-

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

# Load libraries
import math
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier  # Import Decision Tree Classifier
from sklearn.model_selection import train_test_split  # Import train_test_split function
from sklearn import metrics  # Import scikit-learn metrics module for accuracy calculation
import ast
from collections import OrderedDict
from typing import (
    List,
    Dict,
    Tuple
)

from fengkeyleaf.utils import my_collections
from fengkeyleaf.inswitch_anomaly import tree


class Learner:
    @staticmethod
    def convert_to_file(
            t: DecisionTreeClassifier,
            F: List[ str ], fp: str
    ) -> None:
        """

        @param t: Decision Tree.
        @param F: List of feature names.
        @param fp: Output file path.
        """
        # Collect information from the tree.
        # tree_Tree instance
        thresholds: List[ int ] = t.tree_.threshold
        features_in_tree: List[ str ] = [ F[ i ] for i in t.tree_.feature ]
        D: Dict[ str: List[ float ] ] = { f: [ ] for f in F }

        for i, fe in enumerate( features_in_tree ):
            th: int = thresholds[ i ]
            # Skip leaf nodes.
            if th < 0:
                assert th == -2
                continue

            # Add split nodes' information.
            assert t.tree_.feature[ i ] >= 0  # Cannot be -1, which is a leaf node.
            D[ fe ].append( th )

        # Wash and filter the information.
        for k, v in D.items():
            v = [ int( i ) for i in v ]
            for n in v: assert n >= 0, v;

            # https://www.geeksforgeeks.org/python-ways-to-remove-duplicates-from-list/
            # Add the lower bound and upper bound.
            v.append( 0 )
            v.append( int( math.pow( 2, 31 ) ) )

            # Remove duplicates
            v = list( OrderedDict.fromkeys( v ) )
            v.sort()

            if len( v ) <= 0:
                print( "Warning! Empty Feature: " + fp )
                continue

            assert Learner.validate( k, v )
            D[ k ] = v

        # Write the tree to a txt file
        # https://www.w3schools.com/python/python_dictionaries_loop.asp
        with open( fp, "w+" ) as o:
            # Output feature field
            for k, v in D.items():
                o.write( k + " = " )
                o.write( str( v ) )
                o.write( ";\n" )

            # Output tree Field
            tree.get_lineage( t, F, o )

        # o = open( fp, "w+" )
        # o.close()

    @staticmethod
    def validate( k: str, v: List[ float ] ) -> bool:
        """

        @param k: Dict key.
        @param v: Modified list of threshold values.
        @return: Always true to assert.
        """
        # Check the upper bound limit.
        assert v[ -1 ] <= int( math.pow( 2, 31 ) ), v[ -1 ]
        # No empty threshold for a feature.
        assert len( v ) > 0, str( k ) + " | " + str( v )
        # Ascending order.
        assert my_collections.is_monotonic( v )
        return True

    @staticmethod
    def test( f: str, FC: List[ str ] ) -> None:
        """

        @param f: File path to the data set.
        @param FC: List of feature names, excluding the classification label.
        """
        df: pd.DataFrame = pd.read_csv( f )
        print( df )

        X = df[ FC ]
        y = df[ "Outcome" ]

        t: DecisionTreeClassifier = DecisionTreeClassifier().fit( X, y )
        Learner.print_info( t )
        Learner.traverse( t )
        Learner.convert_to_file( t, FC, "./tree.txt" )
        tree.Deparser.deparse( "./tree.txt", FC, Learner._feature_reg( FC ) )

    @staticmethod
    def _feature_reg( F: List[ str ] ) -> str:
        r: str = r"("
        for f in F:
            r += f + "|"

        # Discard the last "|" before appending ")"
        return r[ : len( r ) - 1 ] + ")"

    @staticmethod
    def print_info( t: DecisionTreeClassifier ) -> None:
        print()
        print( "Number of features seen during fit." )
        print( t.n_features_in_ )
        print( "Names of features seen during fit" )
        print( t.feature_names_in_ )
        print( "The number of outputs when fit is performed." )
        print( t.n_outputs_ )
        print( "id of the left child of node i or -1 if leaf node" )
        print( t.tree_.children_left )
        print( "id of the right child of node i or -1 if leaf node" )
        print( t.tree_.children_right )
        print( "feature used for splitting node i" )
        print( t.tree_.feature )
        print( "threshold value at node i" )
        print( t.tree_.threshold )
        print( "the number of training samples reaching node i" )
        print( t.tree_.n_node_samples )
        print( "the impurity at node i" )
        print( t.tree_.impurity )

    # https://scikit-learn.org/stable/auto_examples/tree/plot_unveil_tree_structure.html#sphx-glr-auto-examples-tree-plot-unveil-tree-structure-py
    @staticmethod
    def traverse( clf: DecisionTreeClassifier ):
        n_nodes = clf.tree_.node_count
        children_left = clf.tree_.children_left
        children_right = clf.tree_.children_right
        feature = clf.tree_.feature
        threshold = clf.tree_.threshold

        node_depth = np.zeros( shape = n_nodes, dtype = np.int64 )
        is_leaves = np.zeros( shape = n_nodes, dtype = bool )
        stack = [ (0, 0) ]  # start with the root node id (0) and its depth (0)
        while len( stack ) > 0:
            # `pop` ensures each node is only visited once
            node_id, depth = stack.pop()
            node_depth[ node_id ] = depth

            # If the left and right child of a node is not the same we have a split
            # node
            is_split_node = children_left[ node_id ] != children_right[ node_id ]
            # If a split node, append left and right children and depth to `stack`
            # so we can loop through them
            if is_split_node:
                stack.append( (children_left[ node_id ], depth + 1) )
                stack.append( (children_right[ node_id ], depth + 1) )
            else:
                is_leaves[ node_id ] = True

        print(
            "The binary tree structure has {n} nodes and has "
            "the following tree structure:\n".format( n = n_nodes )
        )
        for i in range( n_nodes ):
            if is_leaves[ i ]:
                print(
                    "{space}node={node} is a leaf node.".format(
                        space = node_depth[ i ] * "\t", node = i
                    )
                )
            else:
                print(
                    "{space}node={node} is a split node: "
                    "go to node {left} if X[:, {feature}] <= {threshold} "
                    "else to node {right}.".format(
                        space = node_depth[ i ] * "\t",
                        node = i,
                        left = children_left[ i ],
                        feature = feature[ i ],
                        threshold = threshold[ i ],
                        right = children_right[ i ],
                    )
                )


if __name__ == '__main__':
    FILE_NAME: str = "./sample_data.csv"
    FILE_NAME_2_FEATURES: str = "./sample_data_2_features.csv"
    FILE_NAME_2_FEATURES_2: str = "./sample_data_2_features_2.csv"

    # Learner.test( FILE_NAME, [
    #         "Weekend", "Reservation", "LongWait"
    #     ] )
    # Learner.test(
    #     FILE_NAME_2_FEATURES, [
    #         "Weekend", "Reservation"
    #     ]
    # )
    Learner.test(
        FILE_NAME_2_FEATURES_2, [
            "Weekend", "Reservation"
        ]
    )
