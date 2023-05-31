# -*- coding: utf-8 -*-

import logging
from typing import (
    List,
    Dict,
    Tuple
)
import pandas
import sklearn
import ast

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

from fengkeyleaf.my_pandas import my_dataframe
import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.io import (
    my_writer,
    my_files
)
from fengkeyleaf.inswitch_anomaly import (
    mapper,
    sketch
)


def reformatting( df: pandas.DataFrame ) -> Tuple[ List[ List[ int ] ], List[ int ] ]:
    """
    formatting from the csv is kinda weird so it is explained here:
    each line looks something like:
        "[sketch]",label
    so, we need to unpack the sketch back into a list from a string
    and then also make sure each part of the sketch is read in as an integer
    """
    data: List[ List[ int ] ] = [ ]
    labels: List[ int ] = [ ]

    for (i, _) in df.iterrows():
        # print( df.loc[ i, sketch_write.RANGE_STR ] )
        # tmp1: List[ str ] = df.loc[ i, sketch_write.RANGE_STR ].strip( '][' ).split( ',' )
        # tmp2: List[ int ] = []
        # for item in tmp1:
        #     tmp2.append( int( item ) )

        labels.append( df.loc[ i, fkl_inswitch.LABEL_STR ] )
        assert labels[ -1 ] == fkl_inswitch.GOOD_LABEL or labels[ -1 ] == fkl_inswitch.BAD_LABEL
        l = df.loc[ i, fkl_inswitch.RANGE_STR ]
        assert isinstance( l, str ) or isinstance( l, list )
        data.append( ast.literal_eval( l ) if isinstance( l, str ) else l )

    return ( data, labels )


# TODO: Put into my_pandas.my_dataframe
def get_data_file(
        fp: str, h: str | None, F: List[ str ]
) -> Tuple[ pandas.DataFrame, pandas.DataFrame, pandas.DataFrame ]:
    """
    Get data columns with wanted feature names
    @param fp: File path to the data set.
    @param h: File path to the header file.
    @param F:List of wanted features.
    @return: ( dataFrame, feature dataFrame, labels )
    """
    df: pandas.DataFrame = mapper.Mapper.mapping( my_dataframe.add_header( h, fp ) )
    assert fkl_inswitch.LABEL_STR in df.columns, str( df ) + "\n" + str( my_dataframe.add_header( h, fp ) )
    for f in F: assert f in df.columns, f + "\n" + str( my_dataframe.add_header( h, fp ).columns ) + "\n" + str( df.columns );

    return _get_data( df, F )


def _get_data(
        df: pandas.DataFrame, F: List[ str ]
) -> Tuple[ pandas.DataFrame, pandas.DataFrame, pandas.DataFrame ]:
    # print( df )
    X: pandas.DataFrame = my_dataframe.get_feature_content( df, fkl_inswitch.LABEL_STR, F )
    # print( df[ csvparaser.LABEL_STR ] )
    # https://stackoverflow.com/a/76294033
    y: pandas.DataFrame = df[ fkl_inswitch.LABEL_STR ].astype( int )

    return ( df, X, y )


def get_data_dataframe(
        df: pandas.DataFrame, F: List[ str ]
) -> Tuple[ pandas.DataFrame, pandas.DataFrame, pandas.DataFrame ]:
    return _get_data( df, F )


# https://towardsdatascience.com/whats-the-meaning-of-single-and-double-underscores-in-python-3d27d57d6bd1
class Evaluator:
    SIGNATURE: str = "_result.csv"

    def __init__( self, l: logging.Logger, D: List[ str ], g: my_dataframe.Builder ) -> None:
        """

        @param l:
        @param D: List of file path to the validation data sets which may be mapped or may not.
        @param g:
        """
        self.l: logging.Logger = l

        self.recorder: my_dataframe.Builder = g
        self.file_list: List[ List[ str ] ] = my_files.get_files_in_dirs( D )
        self._is_writing: bool = False

    # TODO: evaluate() and evaluate_classic can be merged into one, meaning we can give arbitrary features for evaluate(), not the fixed four, scrCount, srcTLS, dstCount, dstTLS.
    # TODO: Could be removed.
    # python3 ./ML/tree.py /home/p4/tutorials/exercises/inswitch_anomaly-data_labeling/test/test_data/sketch.csv /home/p4/tutorials/exercises/inswitch_anomaly-data_labeling/test/tree.txt
    def evaluate(
            self, t: sklearn.tree.DecisionTreeClassifier, tf: str,
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
        self.l.debug( "Evaluate the tree with the 4 features and without the sketch" )

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
                    assert my_writer.get_extension( fp ).lower() == my_files.CSV_EXTENSION
                    data, labels = reformatting( pandas.read_csv( f ) )
                    self.l.debug( my_writer.get_filename( fp ) )
                    self.l.debug( "Accuracy: %.2f%%" % ( t.score( data, labels ) * 100 ) )

    def evaluate_classic(
            self, t: sklearn.tree.DecisionTreeClassifier, tf: str, H: List[ str ],
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
        @param t_data: training data set.
        @param t_labels: testing data set.
        """
        self.l.debug( "Evaluate the tree with wanted features and without the sketch" )
        self.l.debug( "Accuracy of this tree: %.2f%%" % ( t.score( t_data, t_labels ) * 100) )
        self.l.debug( "Verifying the tree with the sketch file: %s" % my_writer.get_filename( tf ) )

        if self._is_writing: self.recorder.add_row_name( my_writer.get_filename( tf ) );

        for i in range( len( self.file_list ) ):
            for fp in self.file_list[ i ]:
                assert my_writer.get_extension( fp ).lower() == my_files.CSV_EXTENSION

                ( df, X, y ) = get_data_file(
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

    def evaluate_sketch(
            self, t: sklearn.tree.DecisionTreeClassifier, tf: str, H: List[ str | None ],
            feature_list: List[ str ], l: int,
            t_data: pandas.DataFrame, t_labels: pandas.DataFrame
    ) -> None:
        """
        Evaluate a tree with the sketch applied.
        And the validation sets are not pre-processed.( mainly feature mapping ).
        Validation features are the same as the ones in the training process.
        @param t: Decision tree classifier.
        @param tf: File path to the tree.
        @param H: List of file paths to the header.
        @param feature_list: List of wanted features.
        @param l: Limitation for the sketch, l empty spots available for each IP container.
        @param t_data: training data set.
        @param t_labels: testing data set.
        """
        self.l.debug( "Evaluate the tree with the sketch of the limitation " + str( l ) )
        self.l.debug( "Accuracy of this tree: %.2f%%" % ( t.score( t_data, t_labels ) * 100) )
        self.l.debug( "Verifying the tree with the sketch file: %s" % my_writer.get_filename( tf ) )

        if self._is_writing: self.recorder.add_row_name( my_writer.get_filename( tf ) );

        for i in range( len( self.file_list ) ):
            s: sketch.Sketch = sketch.Sketch( l )
            b: my_dataframe.Builder = my_dataframe.Builder( C = fkl_inswitch.COLUMN_NAMES )

            for fp in self.file_list[ i ]:
                assert my_writer.get_extension( fp ).lower() == my_files.CSV_EXTENSION

                ( df, X, y ) = get_data_file(
                    fp,
                    H[ i ],
                    feature_list
                )

                for ( idx, series ) in df.iterrows():
                    si: str = series.at[ fkl_inswitch.SRC_ADDR_STR ]
                    di: str = series.at[ fkl_inswitch.DST_ADDR_STR ]
                    # Record p's srcIP and p's dstIP in s.
                    s.add_src( si )
                    s.add_dst( di )

                    b.add_row( str( idx ), [ str( n ) for n in s.getData( si, di ) ] )

                test_file_name: str = my_writer.get_filename( fp )
                self.l.debug( test_file_name )
                # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.predict
                r: float = sklearn.metrics.accuracy_score( y, t.predict( b.to_dataframe() ) )
                self.l.debug( "Accuracy: %.2f%%" % r )

                if self._is_writing: self.recorder.add_column_name( test_file_name );
                if self._is_writing:
                    self.recorder.append_element( str( r ), my_writer.get_filename( tf ), test_file_name )
