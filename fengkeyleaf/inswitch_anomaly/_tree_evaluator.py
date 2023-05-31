# -*- coding: utf-8 -*-

import logging
from typing import (
    List,
    Dict,
    Tuple
)
import pandas
from sklearn.tree import (
    DecisionTreeClassifier
)

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

from fengkeyleaf.my_pandas import my_dataframe
from fengkeyleaf.io import (
    my_writer,
    my_files
)


class Evaluator:
    SIGNATURE: str = "_result.csv"

    def __init__( self, l: logging.Logger, D: List[ str ], g: my_dataframe.Builder ) -> None:
        """
        :param X: array-like of shape (n_samples, n_features)
        :param y: array-like of shape (n_samples,) or (n_samples, n_outputs)
        :param t: decisoin tree
        """
        self.l: logging.Logger = l

        self.recorder: my_dataframe.Builder = g
        self.file_list: List[ List[ str ] ] = my_files.get_files_in_dirs( D )
        self._is_writing: bool = False

    # TODO: evaluate() and evaluate_classic can be merged into one, meaning we can give arbitrary features for evaluate(), not the fixed four, scrCount, srcTLS, dstCount, dstTLS.
    # python3 ./ML/tree.py /home/p4/tutorials/exercises/inswitch_anomaly-data_labeling/test/test_data/sketch.csv /home/p4/tutorials/exercises/inswitch_anomaly-data_labeling/test/tree.txt
    def evaluate(
            self, t: DecisionTreeClassifier, tf: str,
            t_data: List[ List[ int ] ], t_labels: List[ int ]
    ) -> None:
        """
        Standard evaluation where validation sets are pre-processed ( mainly feature mapping ).
        Validation process doesn't involve the sketch.
        @param t: The tree.
        @param tf: Tree file path.
        @param t_data: Tree's training data.
        @param t_labels: Tree's label data
        """
        if len( self.file_list ) <= 0:
            self.l.debug( "Accuracy of this tree: %.2f%%" % (t.score( t_data, t_labels ) * 100) )
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
                    self.l.debug( "Accuracy: %.2f%%" % (t.score( data, labels ) * 100) )

    def evaluate_classic(
            self, t: DecisionTreeClassifier, tf: str, H: List[ str ],
            feature_list: List[ str ],
            t_data: pandas.DataFrame, t_labels: pandas.DataFrame
    ) -> None:
        """
        Standard evaluation where validation sets are not pre-processed ( mainly feature mapping ).
        Validation features are the same as the ones in the training process.
        Validation process doesn't involve the sketch.
        @param t: Decision tree classifier.
        @param tf: File path to the tree.
        @param H: List of file paths to the header.
        @param feature_list: List of wanted features.
        @param L: List of label strings.
        @param t_data: training data set.
        @param t_labels: testing data set.
        """
        self.l.debug( "Accuracy of this tree: %.2f%%" % (t.score( t_data, t_labels ) * 100) )
        self.l.debug( "Verifying the tree with the sketch file: %s" % my_writer.get_filename( tf ) )

        if self._is_writing: self.recorder.add_row_name( my_writer.get_filename( tf ) );

        for i in range( len( self.file_list ) ):
            for fp in self.file_list[ i ]:
                assert my_writer.get_extension( fp ).lower() == my_files.CSV

                (df, X, y) = Tree._get_data(
                    fp,
                    H[ i ],
                    feature_list
                )

                test_file_name: str = my_writer.get_filename( fp )
                self.l.debug( test_file_name )
                result: float = t.score( X, y ) * 100
                self.l.debug( "Accuracy: %.2f%%" % result )

                if self._is_writing: self.recorder.add_column_name( test_file_name );
                if self._is_writing:
                    self.recorder.append_element( str( result ), my_writer.get_filename( tf ), test_file_name )

    def set_is_writing( self, is_writing: bool ) -> None:
        self._is_writing = is_writing

    def evaluate_sketch( self ):

        pass