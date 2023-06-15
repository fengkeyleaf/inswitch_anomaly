# -*- coding: utf-8 -*-

import logging
from typing import (
    List,
    Dict,
    Tuple,
    Set
)
import numpy
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
from fengkeyleaf import my_typing
from fengkeyleaf.utils import my_dict, my_math
from fengkeyleaf.io import (
    my_writer,
    my_files
)
from fengkeyleaf.inswitch_anomaly import (
    mapper,
    sketch,
    sketch_write
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

    for ( i, _ ) in df.iterrows():
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
) -> Tuple[ pandas.DataFrame, pandas.DataFrame, pandas.Series ]:
    """
    Get data columns with wanted feature names
    @param fp: File path to the data set.
    @param h: File path to the header file.
    @param F:List of wanted features.
    @return: ( dataFrame containing the later two, feature dataFrame, labels dataframe )
    """
    df: pandas.DataFrame = mapper.Mapper.mapping( my_dataframe.add_header( h, fp ) )
    assert fkl_inswitch.LABEL_STR in df.columns, str( df ) + "\n" + str( my_dataframe.add_header( h, fp ) )
    for f in F: assert f in df.columns, f + "\n" + str( my_dataframe.add_header( h, fp ).columns ) + "\n" + str( df.columns );

    return _get_data( df, F )


def _get_data(
        df: pandas.DataFrame, F: List[ str ]
) -> Tuple[ pandas.DataFrame, pandas.DataFrame, pandas.Series ]:
    # print( df )
    X: pandas.DataFrame = my_dataframe.get_feature_content( df, fkl_inswitch.LABEL_STR, F )
    # print( df[ csvparaser.LABEL_STR ] )
    # https://stackoverflow.com/a/76294033
    y: pandas.Series = df[ fkl_inswitch.LABEL_STR ].astype( int )

    return ( df, X, y )


def get_data_dataframe(
        df: pandas.DataFrame, F: List[ str ]
) -> Tuple[ pandas.DataFrame, pandas.DataFrame, pandas.Series ]:
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
        self.l.debug( "Evaluate the tree with the 4 features and without the limited sketch" )
        self.l.debug( "Accuracy of this tree: %.2f%%" % ( t.score( t_data, t_labels ) * 100) )
        # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.predict
        # print( self.t.predict( self.X ) )
        # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.score
        self.l.debug( "Verifying the tree with the sketch file: %s" % my_writer.get_filename( tf ) )

        if self._is_writing: self.recorder.add_row_name( my_writer.get_filename( tf ) );

        for F in self.file_list:
            for fp in F:
                with open(
                        fp, encoding = my_files.UTF8,
                        errors = my_files.BACK_SLASH_REPLACE
                ) as f:
                    assert my_writer.get_extension( fp ).lower() == my_files.CSV_EXTENSION

                    test_file_name: str = my_writer.get_filename( fp )
                    self.l.debug( test_file_name )

                    data, labels = reformatting( pandas.read_csv( f ) )
                    result: float = t.score( data, labels ) * 100
                    self.l.debug( "Accuracy: %.2f%%" % result )

                    if self._is_writing: self.recorder.add_column_name( test_file_name );
                    if self._is_writing:
                        self.recorder.append_element( str( result ), my_writer.get_filename( tf ), test_file_name )

    def evaluate_classic(
            self, t: sklearn.tree.DecisionTreeClassifier, tf: str, H: List[ str ],
            feature_list: List[ str ],
            t_data: pandas.DataFrame, t_labels: pandas.Series
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
            is_limited: bool, t_data: pandas.DataFrame, t_labels: pandas.Series
    ) -> None:
        """
        Evaluate a tree with the sketch applied.
        And the validation sets are not pre-processed.( mainly feature mapping ).
        Validation features are the same as the ones in the training process.
        @param t: Decision tree classifier.
        @param tf: File path to the tree.
        @param H: List of file paths to the header.
        @param is_limited: Limitation for the sketch, l empty spots available for each IP container.
        @param t_data: training data set.
        @param t_labels: testing data set.
        """
        if is_limited: self.l.debug( "Evaluate the tree with the sketch limitation optimization process enabled" );
        self.l.debug( "Accuracy of this tree: %.2f%%" % ( t.score( t_data, t_labels ) * 100 ) )
        self.l.debug( "Verifying the tree with the sketch file: %s" % my_writer.get_filename( tf ) )

        if self._is_writing: self.recorder.add_row_name( my_writer.get_filename( tf ) );

        # Go though all test groups.
        for i in range( len( self.file_list ) ):
            # Evaluate with unlimited sketch
            if not is_limited:
                self._evaluate_sketch( t, self.file_list[ i ], -1, tf, H[ i ] )
                continue

            # Evaluate with unlimited sketch and optimization process
            op: _Optimizer = _Optimizer( self.file_list[ i ], self.l )

            # Optimization process.
            while op.has_next():
                l: int = op.next()
                # Iterate each test file in one test group.
                op.add( l, self._evaluate_sketch( t, self.file_list[ i ], l, tf, H[ i ] ) )
                op.find_median( l )

            self.l.debug( "limitation=%d, median accuracy=%.2f%%" % op.find_max() )

    def _evaluate_sketch(
            self, t: sklearn.tree.DecisionTreeClassifier,
            F: List[ str ], l: int, tf: str, h: str
    ) -> List[ float ]:
        """

        @param t: Decision tree classifier.
        @param F: List of test file paths.
        @param l: SKetch limitation
        @param tf: File path to the tree.
        @param h: File path to the header
        @return: List of accuracy numbers for the test files in the file list, F.
        """
        A: List[ float ] = []

        for fp in F:
            sw: sketch_write.SketchWriter = sketch_write.SketchWriter( None, None, False, l, False, self.l.level )

            assert my_writer.get_extension( fp ).lower() == my_files.CSV_EXTENSION
            ( df, _, _ ) = get_data_file(
                fp,
                h,
                fkl_inswitch.PKT_FEATURE_NAMES
            )

            ( _, df_n ) = sw.process( df, None )
            A.append(
                self._record(
                    t, fp, tf, l, df_n
                )
            )

        return A

    def _record(
            self, t: sklearn.tree.DecisionTreeClassifier,
            fp: str, tf: str, l: int, df: pandas.DataFrame
    ) -> float:
        # filename + sketch limitation
        test_file_name: str = my_writer.get_filename( fp ) + ( ( "_limit_of_" + str( l ) ) if l > 0 else "" )
        # https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier.predict
        pre: numpy.ndarray = t.predict( df.drop( columns = [ fkl_inswitch.LABEL_STR ] ) )
        # check inconsistent numbers of samples
        assert my_typing.equals( df[ fkl_inswitch.LABEL_STR ].size, len( pre ) ), "test file: %s, y size: %d, pre size: %d" % ( test_file_name, df[ fkl_inswitch.LABEL_STR ].size, len( pre ))
        r: float = sklearn.metrics.accuracy_score(
            df[ fkl_inswitch.LABEL_STR ].astype( int ),
            pre
        ) * 100

        # Accuracy Logging
        self.l.debug( test_file_name )
        self.l.debug( "Accuracy: %.2f%%" % r )

        # Writing Accuracy logging
        if self._is_writing:
            assert not self.recorder.contains_col_name( test_file_name ), test_file_name
            self.recorder.add_column_name( test_file_name )
        if self._is_writing:
            self.recorder.append_element( str( r ), my_writer.get_filename( tf ), test_file_name )

        return r


class _Optimizer:
    """
    Class to find the optimal sketch limitation, empty spot for each src and dst ips.
    """
    def __init__( self, F: List[ str ], l: logging.Logger ) -> None:
        assert F is not None
        # Search range domain.
        self.range: List[ int ] = _Optimizer._find_range( F )
        self.res: Dict[ int, List[ float ] ] = {}
        self.res_median: Dict[ int, float ] = {}

        self.l: logging.Logger = l
        self.l.debug( "Optimization range: [ %d, %d ]" % ( self.range[ 0 ], self.range[ 1 ] ) )

    # TODO: Empty spot overflow.
    @staticmethod
    def _find_range( F: List[ str ] ) -> List[ int ]:
        """
        Find the search domain range, [ min, max ]
        @param F: A group of data sets.
        @return: [ min, max ], where min is usually 0,
                 max is the maximum number between the max number of src ips and the that of dst ips.
        """
        S_src: Set[ str ] = set()
        S_dst: Set[ str ] = set()
        for f in F:
            for ( _, s ) in pandas.read_csv( f ).iterrows():
                _Optimizer._add( S_src, s.at[ fkl_inswitch.SRC_ADDR_STR ] )
                _Optimizer._add( S_dst, s.at[ fkl_inswitch.DST_ADDR_STR ] )

        # return [ 42, 43 ]
        return [ 0, max( len( S_src ), len( S_dst ) ) ]

    @staticmethod
    def _add( S: Set[ str ], ip: str ) -> None:
        if not ( ip in S ): S.add( ip );

    def has_next( self ) -> bool:
        """
        Tell if there is the next limitation to evaluate.
        @return:
        """
        return self.range[ 0 ] < self.range[ 1 ]

    def next( self ) -> int:
        """
        Get the next limitation if there is a one.
        @return:
        """
        self.range[ 0 ] += ( self.range[ 1 ] - self.range[ 0 ] + 1 ) // 2
        assert self.range[ 0 ] <= self.range[ 1 ]
        return self.range[ 0 ]

    def add( self, l: int, R: List[ float ] ) -> None:
        """
        Add a list of accuracies with the limitation, l, to this optimizer.
        @param l: The limitation.
        @param R: List of accuracies
        """
        assert self.res.get( l ) is None
        self.res[ l ] = R

    def find_median( self, l: int ) -> None:
        """
        Find the median accuracy for the limitation, l.
        @param l: The limitation.
        """
        assert self.res_median.get( l ) is None
        self.res_median[ l ] = my_math.find_median( self.res[ l ] )

    def find_max( self ) -> Tuple[ int, float ]:
        """
        Find the limitation with the maximum median accuracy in this optimizer.
        @return: ( limitation, median accuracy )
        """
        return my_dict.find_max_value( self.res_median )
