# -*- coding: utf-8 -*-

import logging
import math
import unittest
from collections import OrderedDict
from typing import (
    List,
    Dict,
    Tuple
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
    SKETCH_LIMITATION: int = 8

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
        self.recorder: my_dataframe.Builder = my_dataframe.Builder( ll = ll )
        self.e = _tree_evaluator.Evaluator( self.l, D, self.recorder )
        self._is_writing: bool = is_writing
        self.e.set_is_writing( is_writing )

        self.d = d
        self.pd = pd

    def process( self, f: str, df_o: pandas.DataFrame | None, df_n: pandas.DataFrame | None ) -> None:
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
            fkl_inswitch.FEATURE_NAMES
        )

        t = DecisionTreeClassifier().fit( X, y )

        self.e.set_is_writing( True )
        self.e.evaluate_sketch(
            t, f,
            [ None for _ in range( len( self.e.file_list ) ) ],
            fkl_inswitch.FEATURE_NAMES, Tree.SKETCH_LIMITATION,
            X, y
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

    # Initial Test
    # F = [ [ "pkts", "bytes", "ltime"  ] ]
    # L = [ "attack" ]
    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/training_without_sketch/training"
    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/training_without_sketch/validate" ]

    # BoT-IoT
    # F1 = [ "spkts", "dpkts", "sbytes", "dbytes" ]
    # h1 = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/training_without_sketch/training_large"
    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/training_without_sketch/validate_large" ]

    # TON_IoT
    # F2 = [ "src_bytes", "dst_bytes", "src_pkts", "dst_pkts" ]
    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/large_test"

    # UNSW-NB15
    # F3 = [ "sbytes", "dbytes", "Spkts", "Dpkts" ]
    # h3 = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/NUSW-NB15_features_name.csv"
    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/data"

    # L = [ "attack", "label", "Label" ]
    # F = [ F1, F2, F3 ]
    # F = [ fengkeyleaf.csvparaser.SRC_PKTS_STR, fengkeyleaf.csvparaser.SRC_BYTES_STR, fengkeyleaf.csvparaser.DST_PKTS_STR, fengkeyleaf.csvparaser.DST_BYTES_STR ]
    # H = [ h1, None, h3 ]
    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/training_without_sketch/validate_large", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/large_test", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/data" ]

    # Full test
    # Handle NaN
    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/training_without_sketch/data", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/data", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/data" ]

    # fengkeyleaf.tree.Tree( None, da, D, True, 10 ).train( h, H, F )
    def train(
            self, h: str | None, H: List[ str ] | None,
            F: List[ str ] | None = None
    ) -> None:
        """
        Train a tree with designed features. No sketch applied in the validation process.
        The name of the label feature must be Label.
        @param h: File paths to the testing header.
        @param H: List of file paths to the header.
        @param F: List of wanted features.
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
            self.e.evaluate_classic( t, f, H, F, X, y )

        if self._is_writing:
            self.recorder.to_csv( self.pd + _tree_evaluator.Evaluator.SIGNATURE )
            self.recorder.reset()


class _Tester( unittest.TestCase ):
    IS_WRITING: bool = True

    h1: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
    h3: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/NUSW-NB15_features_name.csv"
    H_FULL: List[ str | None ] = [ None, None, None ]

    # Feature name list
    F_S: List[ str ] = [ fkl_inswitch.SRC_COUNT_STR, fkl_inswitch.SRC_TLS_STR, fkl_inswitch.DST_COUNT_STR, fkl_inswitch.DST_TLS_STR ]
    F_S_O: List[ str ] = [ fkl_inswitch.RANGE_STR ]

    dt1_o: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches"
    dt2_o: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/sketches"
    dt3_o: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/sketches"
    V_FULL_O: List[ str ] = [ dt1_o, dt2_o, dt3_o ]

    dt1: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches_new"
    dt2: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/sketches_new"
    dt3: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/sketches_new"
    V_FULL: List[ str ] = [ dt1, dt2, dt3 ]

    # Validation with wanted features and unlimited sketch
    # @unittest.skip
    def test_bot_lot_wanted_unlimited_sketch( self ) -> None:
        dt: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches_new"
        V: List[ str ] = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches_new" ]
        H: List[ str | None ] = [ None ]

        # Tree( None, dt, V, True, 10 ).train( None, H, _Tester.F_S )
        # Tree( None, _Tester.dt1_o, _Tester.V_FULL_O, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S_O )
        Tree( None, _Tester.dt1, _Tester.V_FULL, True, 10 ).train( None, _Tester.H_FULL, _Tester.F_S )

    # @unittest.skip
    def test_ton_lot_wanted_unlimited_sketch( self ) -> None:
        # Tree( None, _Tester.dt2_o, _Tester.V_FULL_O, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S_O )
        Tree( None, _Tester.dt2, _Tester.V_FULL, True, 10 ).train( None, _Tester.H_FULL, _Tester.F_S )

    # @unittest.skip
    def test_unsw_nb15_wanted_unlimited_sketch( self ) -> None:
        # Tree( None, _Tester.dt3_o, _Tester.V_FULL_O, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S_O )
        Tree( None, _Tester.dt3, _Tester.V_FULL, True, 10 ).train( None, _Tester.H_FULL, _Tester.F_S )

    dt1_limited: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches_new_balancing_limited"
    dt2_limited: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/sketches_new_balancing_limited"
    dt3_limited: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/sketches_new_balancing_limited"
    V_FULL_limited: List[ str ] = [
        dt1_limited, dt2_limited, dt3_limited
    ]

    # TODO: Go over the code logic before running.
    # Validation with wanted features and limited sketch
    @unittest.skip
    def test_bot_lot_wanted_limited_sketch( self ) -> None:
        # Training is unlimited, but validation is limited.
        Tree( None, _Tester.dt1, _Tester.V_FULL_limited, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S )

    @unittest.skip
    def test_ton_lot_wanted_limited_sketch( self ) -> None:
        Tree( None, _Tester.dt2, _Tester.V_FULL_limited, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S )

    @unittest.skip
    def test_unsw_nb15_wanted_limited_sketch( self ):
        Tree( None, _Tester.dt3, _Tester.V_FULL_limited, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S )


if __name__ == '__main__':
    unittest.main()
