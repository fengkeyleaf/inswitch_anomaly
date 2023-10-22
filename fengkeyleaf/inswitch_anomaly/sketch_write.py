# -*- coding: utf-8 -*-

import logging
from typing import List,Tuple
import pandas
from pandas import DataFrame

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
            srcCount | srcTLS | dstCount | dstTLS | Label -> Columns
    Rows |
         v
    """
    # Sketch file config
    SKETCH_FOLDER_NAME: str = "/sketches/"
    SKETCH_SIGNATURE: str = "_sketch.csv"
    SKETCH_SIGNATURE_NEW: str = "_sketch_new.csv"

    def __init__(
            self, dir: str, pdir: str, lim: int = -1,
            is_writing_sketch: bool = True, ll: int = logging.INFO
    ) -> None:
        """

        @param dir: Directory to re-formatted pkt csv files.
        @param pdir: Directory to original pkt csv files.
        @param lim: Sketch limitation.
        @param is_writing_sketch: Tell if writing the test result to a file.
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
        self.lim: int = lim

        # I/O config
        self.is_writing_sketch: bool = is_writing_sketch
        self.dir = dir
        self.pdir = pdir

        # Logging and checker
        self.l: logging.Logger = my_logging.get_logger( ll )

    # TODO: return ( data, labels )
    def process( self, df: DataFrame, f: str ) -> Tuple[ DataFrame, DataFrame ]:
        """
        Process pre-processed csv pkt files and balancing the data set,
        and track some features with the sketch.
        @param df:
        @param f: File path to the original pkt csv file.
        @return:
        """
        # Reset data
        self.data = []
        self.labels = []
        self.b = my_dataframe.Builder( C = fkl_inswitch.COLUMN_NAMES )
        self.idx = 0  # Dataframe index for the new format

        self._process( df )

        assert not self.is_writing_sketch or f is not None
        return self._write( f )

    def _process( self, df: DataFrame ) -> None:
        """
        Extract features from pkts and store the information into the sketch.
        Also, Update the sketch with the data sampling applied.
        @param df: Pre-processed ptt dataframe.
        """
        assert len( self.data ) <= 0 and len( self.labels ) <= 0
        assert self.b.size_row() <= 0 and self.b.size() <= 0

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
            self._add( s.get_data( si, di ), df.at[ idx, fkl_inswitch.LABEL_STR ] )

        # return D
        # Size info, i.e. limitation info
        self.l.debug( "Sketch size: src dict=%d, dst dict=%d" % s.size() )

    def _add(
            self, D: List[ int ], l: int
    ) -> None:
        """
        Add a pkt sketch record into the data container.
        @param D: List of sketch data for a pkt record.
        @param l: Label, 0 or 1.
        @return:
        """
        # then d <- [
        #   			[ srcCount in s, srcTL in s, dstCount in s, dstTLS in s ],
        #               label
        #   	    ]
        # Old format
        self.data.append( D )
        self.labels.append( l )
        assert len( self.data ) == len( self.labels )

        # New format
        # Add the four features
        D_t: List = list( D )
        # Add the lable.
        D_t.append( l )
        # Add the data record into the dataframe builder.
        # index -> [ srcCount in s, srcTL in s, dstCount in s, dstTLS in s, label ]
        self.b.add_row( str( self.idx ), [ str( n ) for n in D_t ] )
        self.idx += 1
        assert self.idx == self.b.size_row(), "%d | %d" % (self.idx, self.b.size_row())
        assert self.b.size_row() == len( self.data ), "%d | %d" % (self.b.size_row(), len( self.data ))

    def _write( self, f: str ) -> Tuple[ DataFrame, DataFrame ]:
        """
        Write the sketches with labels to a file.
        @param f: File path where the original data file is located.
        @return ( sketch dataframe in the old format, sketch dataframe in the new format )
        @rtype: Tuple[ DataFrame, DataFrame ]
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
        if not self.is_writing_sketch: return;

        # Write to file
        d: str = my_writer.get_dir( f ) + SketchWriter.SKETCH_FOLDER_NAME
        my_writer.make_dir( d )
        fn: str = my_writer.get_filename( f )
        f = d + fn + SketchWriter.SKETCH_SIGNATURE

        self.l.info( "Writing old sketch to:\n" + f )
        df_o.to_csv(
            f, index = False
        )
        self.l.info( "Writing new sketch to:\n" + d + fn + SketchWriter.SKETCH_SIGNATURE_NEW )
        df_n.to_csv(
            d + fn + SketchWriter.SKETCH_SIGNATURE_NEW, index = False
        )

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



