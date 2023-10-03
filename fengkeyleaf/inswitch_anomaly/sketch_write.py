# -*- coding: utf-8 -*-

import logging
import random
from typing import (
    List,
    Tuple
)
import unittest

import numpy
import pandas
from pandas import (
    DataFrame
)

"""
file: sketch_write.py
description: file to do sketch building and write results to a csv file
language: python3 3.11.3
author: @sean bergen,
        @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging
from fengkeyleaf.my_pandas import my_dataframe
from fengkeyleaf.io import ( my_writer, my_files )
from fengkeyleaf import my_typing
import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.inswitch_anomaly import sketch


# https://www.geeksforgeeks.org/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python/
class SketchWriter:
    """
    Generate sketch csv files to train trees.
    Format of sketch file:
            srcCount srcTLS dstCount dstTLS Label -> Columns
    Rows |
         v
    """
    FOLDER_NAME: str = "/sketches/"
    SIGNATURE: str = "_sketch.csv"
    SIGNATURE_NEW: str = "_sketch_new.csv"

    def __init__(
            self, dir: str, pdir: str,
            is_not_balancing: bool = False, lim: int = -1,
            is_writing: bool = True, ll: int = logging.INFO
    ) -> None:
        """

        @param dir: Directory to re-formatted pkt csv files.
        @param pdir: Directory to original pkt csv files.
        @param is_not_balancing: Tell if the data sampling is enabled or not.
        @param lim: Sketch limitation.
        @param is_writing: Tell if writing the test result to a file.
        @param ll: Logging level.
        """
        self.data: List[ List[ int ] ] = []
        self.labels: List[ int ] = []
        # Data in the Builder will not be cleared after training.
        self.b: my_dataframe.Builder = None

        self.idx: int = 0
        # gc <- 0 // good pkt count
        self.gc: int = 0
        # bc <- 0 // bad pkt count
        self.bc: int = 0
        # Sketch config
        self.is_not_balancing: bool = is_not_balancing
        self.lim: int = lim

        self.is_writing: bool = is_writing
        self.dir = dir
        self.pdir = pdir

        self.l: logging.Logger = my_logging.get_logger( ll )
        self._c: SketchWriter._Checker = self._Checker( self.l )

    # TODO: return ( data, labels )
    def process( self, df: DataFrame, f: str ) -> Tuple[ DataFrame, DataFrame ]:
        """
        Process pre-processed csv pkt files and balancing the data set,
        and track some features with the sketch.
        @param df:
        @param f: File path to the original pkt csv file.
        @return:
        """
        if self.is_not_balancing: self.l.info( "Balancing is turned off in SketchWriter." );

        self._counting( df )
        self._process( df )

        assert not self.is_writing or f is not None
        return self._write( f )

    # Algorithm DATASAMPLING( P )
    # Input. P is input data set to generate a sketch csv file. Assuming we have labled data as our file.
    # Output. Balanced sketch csv file to train a decision tree.
    def _process( self, df: DataFrame ) -> None:
        """
        Extract features from pkts and store the information into the sketch.
        Also Update the sketch with the data sampling applied.
        @param df:
        """
        assert len( self.data ) <= 0 and len( self.labels ) <= 0
        assert self.b.size_row() <= 0 and self.b.size() <= 0
        assert self._c.setLen( my_dataframe.get_row_size( df ) )

        # gdp <- gc / len( P ) // good Drop Percent
        gdp: float = self.gc / my_dataframe.get_row_size( df )
        # bdp <- bc / len( P ) // bad Drop Percent
        bdp: float = self.bc / my_dataframe.get_row_size( df )
        if not self.is_not_balancing:
            self.l.debug( "gdp( bad Drop Percent ): %f, bdp( bad Drop Percent ): %f" % ( gdp, bdp ) )

        # s <- sketch without the limitation threshold.
        s: sketch.Sketch = sketch.Sketch( self.lim )
        # D <- list of sketch data formatted as [ [ srcCount, srcTLS, dstCount, dstTLS ], label ]

        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iterrows.html
        # for every pkt, p, in P
        for ( idx, _ ) in df.iterrows():
            # Increment the TLS of every tracked ip in s.
            # None of element in the sketch right now, so no effect execute this step first.
            # s.post_process()

            si: str = df.at[ idx, fkl_inswitch.SRC_ADDR_STR ]
            di: str = df.at[ idx, fkl_inswitch.DST_ADDR_STR ]
            # Record p's srcIP and p's dstIP in s.
            s.add_src( si )
            s.add_dst( di )

            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.at.html#pandas.DataFrame.at
            assert df.at[ idx, fkl_inswitch.LABEL_STR ] == fkl_inswitch.BAD_LABEL or df.at[ idx, fkl_inswitch.LABEL_STR ] == fkl_inswitch.GOOD_LABEL, df.at[ idx, fkl_inswitch.LABEL_STR ]
            self._balancing( s.getData( si, di ), df.at[ idx, fkl_inswitch.LABEL_STR ], gdp, bdp )

        assert self._c.isBalanced( s )
        # return D

    def _write( self, f: str ) -> Tuple[ DataFrame, DataFrame ]:
        """
        Write the sketches with labels to a file.
        @param f: File path where the result sketch file is written.
        """
        if len( self.data ) == 0 or len( self.labels ) == 0:
            self.l.warning( "Sketch: No data written to the file!" )

        # https://www.geeksforgeeks.org/create-a-pandas-dataframe-from-lists/
        df_o: DataFrame = DataFrame( {
            fkl_inswitch.RANGE_STR: self.data,
            fkl_inswitch.LABEL_STR: self.labels
        } )
        df_n: DataFrame = self.b.to_dataframe()

        assert _Comparator( self, df_n ).compare()

        self._writing_to_file( f, df_o, df_n )
        return ( df_o, df_n )

    def _writing_to_file(
            self, f: str, df_o: DataFrame, df_n: DataFrame
    ) -> None:
        if not self.is_writing: return;

        # Write to file
        d: str = my_writer.get_dir( f ) + SketchWriter.FOLDER_NAME
        my_writer.make_dir( d )
        fn: str = my_writer.get_filename( f )
        f = d + fn + SketchWriter.SIGNATURE

        self.l.info( "Writing old sketch to:\n" + f )
        df_o.to_csv(
            f, index = False
        )
        self.l.info( "Writing new sketch to:\n" + d + fn + SketchWriter.SIGNATURE_NEW )
        df_n.to_csv(
            d + fn + SketchWriter.SIGNATURE_NEW, index = False
        )

    def _counting( self, df: DataFrame ) -> None:
        """
        Count good pkts and bad pkts.
        @param df:
        """
        # Reset data
        self.data = []
        self.labels = []
        self.gc = 0
        self.bc = 0
        self.b = my_dataframe.Builder( C = fkl_inswitch.COLUMN_NAMES )
        self.idx = 0

        # for every pkt, p, in P
        for ( i, s ) in df.iterrows():
            # do if p is a good one
            if df.at[ i, fkl_inswitch.LABEL_STR ] == fkl_inswitch.GOOD_LABEL:
                # then gc++
                self.gc += 1
            # else bc++
            else:
                assert df.at[ i, fkl_inswitch.LABEL_STR ] == fkl_inswitch.BAD_LABEL
                self.bc += 1

        assert self.gc + self.bc == my_dataframe.get_row_size( df )
        if not self.is_not_balancing:
            self.l.debug( "gc(good count): %d, bc(bad count): %d, tc(total count): %d" % ( self.gc, self.bc, my_dataframe.get_row_size( df ) ) )

    def _balancing( self, D: List[ int ], l: int, gdp: float, bdp: float ) -> None:
        assert 0 <= gdp <= 1
        assert 0 <= bdp <= 1
        assert l == fkl_inswitch.GOOD_LABEL or l == fkl_inswitch.BAD_LABEL

        # ifAddGood <- p is a good one and randDoube() > gdp
        if_add_good: bool = l == fkl_inswitch.GOOD_LABEL and random.random() > gdp
        # ifAddBad <- p is a bad one and randDoube() > bdp
        if_add_bad: bool = l == fkl_inswitch.BAD_LABEL and random.random() > bdp
        # if ifAddGood or ifAddBad
        if self.is_not_balancing or ( if_add_good or if_add_bad ):
            # then d <- [
            #   			[ srcCount in s, srcTL in s, dstCount in s, dstTLS in s ],
            #               label
            #   	    ]
            self.data.append( D )
            self.labels.append( l )
            assert len( self.data ) == len( self.labels )

            D_t: List = list( D )
            D_t.append( l )
            self.b.add_row( str( self.idx ), [ str( n ) for n in D_t ] )
            self.idx += 1
            assert self.idx == self.b.size_row(), "%d | %d" % ( self.idx, self.b.size_row() )
            assert self.b.size_row() == len( self.data ), "%d | %d" % ( self.b.size_row(), len( self.data ) )


            # Record actual good pkts.
            if if_add_good:
                assert l == fkl_inswitch.GOOD_LABEL
                self._c.addGood()
            if if_add_bad:
                assert l == fkl_inswitch.BAD_LABEL
                self._c.addBad()

    def train( self ) -> None:
        """
        Train sketch with processed pkt data sets.
        Data sets may include synthesised good pkts or may not.
        """
        self.l.info( "Start processing from training sketch" )

        for fp in my_files.get_files_in_dir( self.dir ):
            self.process( pandas.read_csv( fp ), self.pdir + my_writer.get_filename( fp ) )

    class _Checker:
        def __init__( self, l: logging.Logger ):
            self.tc: int = 0 # total pkt count
            self.gc: int = 0 # actual good count
            self.bc: int = 0

            self.l = l

        def isBalanced( self, s: sketch.Sketch ) -> bool:
            # Balancing info
            self.l.info(
                "R of gc: %0.2f, R of bc: %.2f, gc: %d, bc: %d, tc: %d" % (
                    self.gc / self.tc, self.bc / self.tc, self.gc, self.bc, self.tc
                )
            )

            # Size info, i.e. limitation info
            self.l.debug( "Sketch size: src dict=%d, dst dict=%d" % s.size() )
            return True

        def addGood( self ) -> bool:
            self.gc += 1
            return True

        def setLen( self, tc: int ) -> bool:
            self.tc = tc
            return True

        def addBad( self ) -> None:
            self.bc += 1


class _Comparator:
    """
    Class to compare two sketch data sets to see if they're the same.
    One set is generated by putting all features in one list,
    the other is by putting them into separate columns.
    """
    def __init__( self, s: SketchWriter, df: pandas.DataFrame ) -> None:
        self.D: List[ List[ int ] ] = s.data
        self.L: List[ int ] = s.labels
        self.df: pandas.DataFrame = df

    def compare( self ) -> bool:
        assert len( self.D ) == len( self.L )
        assert len( self.L ) == my_dataframe.get_row_size( self.df ), str( len( self.L ) ) + "| " + str( my_dataframe.get_row_size( self.df ) )

        for ( i, s ) in self.df.iterrows():
            idx: int = int( i )
            assert len( self.D[ idx ] ) == len( fkl_inswitch.SKETCH_FEATURE_NAMES ), str( self.D[ idx ] ) + " | " + str( s )

            # Check if all features are the same.
            for j in range( len( self.D[ idx ] ) ):
                assert my_typing.equals( self.D[ idx ][ j ], int( s.at[ fkl_inswitch.SKETCH_FEATURE_NAMES[ j ] ] ) ), ("row(idx-val): %d - %s | col(idx-val): %d - %s\n%s\n%s") % (idx, self.D[ idx ][ j ], j, s.at[ fkl_inswitch.SKETCH_FEATURE_NAMES[ j ] ], str( self.D[ idx ] ), str( s ))

            # Check if the label is the same.
            assert my_typing.equals( int( self.L[ idx ] ), int( s.at[ fkl_inswitch.LABEL_STR ] ) )

        return True



