# -*- coding: utf-8 -*-

import logging
import random
from typing import List
import pandas

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
from fengkeyleaf import annotations
import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.inswitch_anomaly import sketch


# https://www.geeksforgeeks.org/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python/
class SketchWriter:
    """
    Generate sketch csv files to train trees.
    Format of sketch file:
            srcCount | srcTLS | dstCount | dstTLS | Label -> Columns
    Rows |
         v
    """
    # Sketch file config
    SKETCH_FOLDER_NAME: str = "/sketches/"
    SKETCH_SIGNATURE: str = "_sketch.csv"

    # Balanced original reformatted file config
    BALANCED_FOLDER_NAME: str = "/balanced_reformatted/"
    BALANCED_SIGNATURE: str = "_balanced_reformatted.csv"

    def __init__(
            self, dir: str, pdir: str,
            is_not_balancing: bool = False, lim: int = -1,
            is_writing_sketch: bool = True, is_writing_balanced: bool = False,
            ll: int = logging.INFO
    ) -> None:
        """

        @param dir: Directory to re-formatted pkt csv files.
        @param pdir: Directory to original pkt csv files.
        @param is_not_balancing: Tell if the data sampling is enabled or not.
        @param lim: Sketch limitation.
        @param is_writing_sketch: Tell if writing the test result to a file.
        @param ll: Logging level.
        """
        # Data in the Builder will not be cleared after training.
        self.b: my_dataframe.Builder = None
        self.idx: int = 0

        # Data sampling/balancing setting
        # gc <- 0 // good pkt count
        self.gc: int = 0
        # bc <- 0 // bad pkt count
        self.bc: int = 0
        # Sketch config
        self.is_not_balancing: bool = is_not_balancing
        self.lim: int = lim

        # I/O config
        self.is_writing_sketch: bool = is_writing_sketch
        self.dir = dir
        self.pdir = pdir
        self.is_writing_balanced: bool = is_writing_balanced

        # Logging and checker
        self.l: logging.Logger = my_logging.get_logger( ll )

    def process( self, df: pandas.DataFrame, f: str ) -> pandas.DataFrame:
        """
        Process pre-processed csv pkt files and balancing the data set,
        and track some features with the sketch.
        @param df:
        @param f: File path to the original pkt csv file.
        @return:
        """
        if self.is_not_balancing: self.l.info( "Balancing is turned off in SketchWriter." );

        self._counting( df )
        self._write_balanced(
            self._process( df ),
            f
        )

        assert not self.is_writing_sketch or f is not None
        return self._write( f )

    # Algorithm DATASAMPLING( P )
    # Input. P is input data set to generate a sketch csv file. Assuming we have labled data as our file.
    # Output. Balanced sketch csv file to train a decision tree.
    def _process( self, df: pandas.DataFrame ) -> pandas.DataFrame:
        """
        Extract features from pkts and store the information into the sketch.
        Also, Update the sketch with the data sampling applied.
        @param df: Pre-processed ptt dataframe.
        """
        assert self.b.size_row() <= 0 and self.b.size() <= 0

        # gdp <- gc / len( P ) // good Drop Percent
        gdp: float = self.gc / my_dataframe.get_row_size( df )
        # bdp <- bc / len( P ) // bad Drop Percent
        bdp: float = self.bc / my_dataframe.get_row_size( df )
        if not self.is_not_balancing:
            self.l.debug( "gdp( bad Drop Percent ): %f, bdp( bad Drop Percent ): %f" % ( gdp, bdp ) )

        # s <- sketch without the limitation threshold.
        s: sketch.Sketch = sketch.Sketch( self.lim )
        # D <- list of sketch data formatted as [ [ srcCount, srcTLS, dstCount, dstTLS ], label ]

        L: List[ int ] = []
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
            if not self._balancing( s.get_data( si, di ), df.at[ idx, fkl_inswitch.LABEL_STR ], gdp, bdp ):
                L.append( idx )

        return df.drop( L )
        # return D

    def _write_balanced( self, df: pandas.DataFrame, f: str ) -> None:
        """
        Write balanced reformatted pkt dataframe into a csv file.
        @param df: Balanced reformatted pkt dataframe.
        @param f: File path where the original data file is located.
        @return:
        """
        # Not save the balanced data if we don't want to or,
        # data balancing is turned off at the first place.
        if not self.is_writing_balanced or self.is_not_balancing: return;

        # Write to file
        d: str = my_writer.get_dir( f ) + SketchWriter.BALANCED_FOLDER_NAME
        my_writer.make_dir( d )
        fn: str = my_writer.get_filename( f )
        f = d + fn + SketchWriter.BALANCED_SIGNATURE

        self.l.info( "Writing balanced re-formatted original dataset to:\n" + f )
        df.to_csv(
            f, index = False
        )

    def _write( self, f: str ) -> pandas.DataFrame:
        """
        Write the sketches with labels to a file.
        @param f: File path where the original data file is located.
        @return ( sketch dataframe in the old format, sketch dataframe in the new format )
        @rtype: DataFrame
        """
        # https://www.geeksforgeeks.org/create-a-pandas-dataframe-from-lists/
        df: pandas.DataFrame = self.b.to_dataframe()

        if self.is_writing_sketch:
            # Write to file
            fp: str = fkl_inswitch.get_output_file_path(
                f, SketchWriter.SKETCH_FOLDER_NAME, SketchWriter.SKETCH_SIGNATURE
            )
            self.l.info( "Writing new sketch to:\n" + fp )
            df.to_csv( fp, index = False )

        return df

    def _counting( self, df: pandas.DataFrame ) -> None:
        """
        Count good pkts and bad pkts.
        @param df:
        """
        # Reset data
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
            self.l.debug(
                "gc(good count): %d, bc(bad count): %d, tc(total count): %d" % (
                    self.gc, self.bc, my_dataframe.get_row_size( df )
                )
            )

    def _balancing(
            self, D: List[ int ], l: int, gdp: float, bdp: float
    ) -> bool:
        """
        Data balancing process.
        @param D: List of sketch data for a pkt record.
        @param l: Label, 0 or 1.
        @param gdp: Good pkt probability.
        @param bdp: Bad pkt probability.
        @return: To tell whether to add this pkt record or not.
        """
        assert 0 <= gdp <= 1
        assert 0 <= bdp <= 1
        assert l == fkl_inswitch.GOOD_LABEL or l == fkl_inswitch.BAD_LABEL

        # ifAddGood <- p is a good one and randDoube() > gdp
        if_add_good: bool = l == fkl_inswitch.GOOD_LABEL and random.random() > gdp
        # ifAddBad <- p is a bad one and randDoube() > bdp
        if_add_bad: bool = l == fkl_inswitch.BAD_LABEL and random.random() > bdp
        # if ifAddGood or ifAddBad
        # IF START
        if self.is_not_balancing or ( if_add_good or if_add_bad ):
            # then d <- [
            #   			[ srcCount in s, srcTL in s, dstCount in s, dstTLS in s ],
            #               label
            #   	    ]

            D_t: List = list( D )
            D_t.append( l )
            self.b.add_row( str( self.idx ), [ str( n ) for n in D_t ] )
            self.idx += 1
            assert self.idx == self.b.size_row(), "%d | %d" % ( self.idx, self.b.size_row() )

            return True
        # IF END

        return False

    @annotations.deprecated
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

        def _addGood( self ) -> bool:
            self.gc += 1
            return True

        def _addBad( self ) -> None:
            self.bc += 1

        def setLen( self, tc: int ) -> bool:
            self.tc = tc
            return True

        def count( self, l: int, is_good: bool, is_bad: bool ) -> bool:
            # Record actual good pkts and bad pkts, i.e. count their numbers.
            if is_good:
                assert l == fkl_inswitch.GOOD_LABEL
                self._addGood()
            if is_bad:
                assert l == fkl_inswitch.BAD_LABEL
                self._addBad()

            return True



