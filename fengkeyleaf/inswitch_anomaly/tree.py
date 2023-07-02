# -*- coding: utf-8 -*-

import logging
import math
from collections import OrderedDict
from typing import (
    List,
    Dict,
    Tuple,
    Any
)
import numpy as np
import pandas
import sklearn.tree
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

__version__ = "1.0"


from fengkeyleaf.logging import my_logging
from fengkeyleaf.io import (
    my_writer,
    my_files
)
from fengkeyleaf.utils import my_collections
from fengkeyleaf.my_pandas import my_dataframe
import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.inswitch_anomaly import _tree_evaluator


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
    FOLDER_NAME: str = "/trees/"
    SIGNATURE: str = "_tree.txt"

    def __init__(
            self, d: str | None, pd: str | None,
            D: List[ str ], is_writing: bool = False,
            ll: int = logging.INFO
    ) -> None:
        """

        @param d: Directory to pkt sketch csv files.
        @param pd: Directory to original pkt csv files.
        @param D: List of directories to the processed data sets to test trees.
        @param ll: logging level
        """
        self.l = my_logging.get_logger( ll )
        # Record accuracies computed by one data set as training set and the other as validation set.
        self.acc_rec: my_dataframe.Builder = my_dataframe.Builder( ll = ll )
        # Record sketch limitation optimization data.
        self.lim_opti_rec: my_dataframe.Builder = my_dataframe.Builder( ll = ll )

        self.e = _tree_evaluator.Evaluator( self.l, D, self.acc_rec, self.lim_opti_rec )
        self._is_writing: bool = is_writing
        self.e.set_is_writing( is_writing )

        self.d = d
        self.pd = pd

    def process(
            self, f: str,
            df_o: pandas.DataFrame | None, df_n: pandas.DataFrame | None
    ) -> None:
        """
        Process pkt sketch csv file and train a tree.
        @param df_o: Pre-processed sketch dataframe, list form.
        @param df_n: Pre-processed sketch dataframe, individual column.
        @param f: File path to the original csv pkt file.
        """
        if df_o is not None: self.get_tree_old( f, *_tree_evaluator.reformatting( df_o ) );
        if df_n is not None: self.get_tree_new( f, df_n );

    def get_tree_new( self, f: str, df: pandas.DataFrame ) -> None:
        d: str = my_writer.get_dir( f ) + Tree.FOLDER_NAME
        my_writer.make_dir( d )
        f = d + my_writer.get_filename( f ) + Tree.SIGNATURE
        self.l.info( "tree: " + f )

        assert my_writer.get_extension( f ).lower() == my_files.CSV_EXTENSION, my_writer.get_extension( f ).lower()
        ( df, X, y ) = _tree_evaluator.get_data_dataframe(
            df,
            fkl_inswitch.SKETCH_FEATURE_NAMES
        )

        t = DecisionTreeClassifier().fit( X, y )

        self.e.set_is_writing( True )
        # TODO: Check parameters.
        self.e.evaluate_sketch(
            t, f,
            [ None for _ in range( len( self.e.file_list ) ) ],
            X, y,
            {
                fkl_inswitch.IS_OPTIMIZING_STR: False
            }
        )

        # TODO: Missing converting the tree into a txt file format.

    # TODO: Return a DecisionTreeClassifier.
    def get_tree_old( self, f: str, data, labels ):
        """
        Train a tree ( DecisionTreeClassifier ) and Convert it into a txt file format,
        read by p4 program
        @param f:
        @param data:
        @param labels:
        """
        d: str = my_writer.get_dir( f ) + Tree.FOLDER_NAME
        my_writer.make_dir( d )
        f = d + my_writer.get_filename( f ) + Tree.SIGNATURE
        self.l.info( "tree: " + f )

        decision_tree = DecisionTreeClassifier()
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

    @staticmethod
    def _sketches( c: Dict[ str, Any ] ) -> bool:
        return c is not None and \
            c.get( fkl_inswitch.IS_SKETCHING_STR ) is not None and c.get( fkl_inswitch.IS_SKETCHING_STR )

    def _is_writing_sketch_opti( self, c: Dict[ str, Any ] ) -> bool:
        return self._is_writing and \
            Tree._sketches( c ) and \
            c.get( fkl_inswitch.IS_OPTIMIZING_STR ) is not None and c.get( fkl_inswitch.IS_OPTIMIZING_STR )

    def train(
            self, h: str | None, H: List[ str | None ],
            F: List[ str ] | None = None,
            sketch_config: Dict[ str, Any ] | None = None
    ) -> None:
        """
        Train a tree with designed features. No sketch applied in the validation process.
        The name of the label feature must be Label.
        @param h: File paths to the testing header.
        @param H: List of file paths to the header.
        @param F: List of wanted features.
        @param is_optimizing: Tell if Sketch limitation optimization is enabled.
        @param sketch_config: Sketch configuration dict.
               {
                    fkl_inswitch.IS_SKETCHING_STR: bool,
                    fkl_inswitch.IS_OPTIMIZING_STR: bool,
                    fkl_inswitch.LIMITATION_STR: int,
                    fkl_inswitch.OPTI_FUNCTION_CONFIG_STR: int,
                }
                Parameters other than shown above are useless.
        """
        self.l.info( "Normally training tree......" )

        files: List[ str ] = my_files.get_files_in_dir( self.pd )
        assert len( H ) == len( self.e.file_list ), str( len( H ) ) + " | " + str( len( self.e.file_list ) )

        if len( files ) <= 0:
            self.l.warning( "Empty data sets provided!\n" + self.pd )

        for f in files:
            self.l.debug( "Processing data set file: " + my_writer.get_filename( f ) )
            assert my_writer.get_extension( f ).lower() == my_files.CSV_EXTENSION

            ( df, X, y ) = _tree_evaluator.get_data_file( f, h, F )
            self.l.debug( "DataFrame:\n" + str( df ) )
            self.l.debug( "Training:\n" + str( X ) )
            self.l.debug( "Testing:\n" + str( y ) )

            t: DecisionTreeClassifier = DecisionTreeClassifier().fit( X, y )
            self.e.set_is_writing( True )
            # Validate trees with unlimited or limited sketch.
            if Tree._sketches( sketch_config ):
                self.e.evaluate_sketch(
                    t, f, H, X, y,
                    sketch_config
                )
            else: self.e.evaluate_classic( t, f, H, F, X, y );

            # Write limitation optimization results per training file.
            if self._is_writing_sketch_opti( sketch_config ):
                # Output filename: filename of the training set  + "_ske_opti_result.csv"
                self.lim_opti_rec.to_csv(
                    "{}/{}{}".format(
                        self.pd,
                        my_writer.get_filename( f ),
                        _tree_evaluator.Evaluator.SKETCH_LIMI_OPTI_SIGNATURE
                    )
                )
                self.lim_opti_rec.reset()

        # Write accuracy results
        if self._is_writing:
            self.acc_rec.to_csv( self.pd + _tree_evaluator.Evaluator.ACCU_SIGNATURE )
            self.acc_rec.reset()


class _Optimizer:
    def __init__( self, r: my_dataframe.Builder | None = None, f: str | None = None ):

        pass

    def optimize( self ) -> Tuple[ int, float ]:

        pass
