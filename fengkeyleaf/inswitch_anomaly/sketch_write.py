# -*- coding: utf-8 -*-

import logging
import random
from typing import (
    List,
    Tuple
)
import unittest
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
import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.inswitch_anomaly import sketch

RANGE_STR = "range"
GOOD_LABEL = 0
BAD_LABEL = 1 # attack pkt


# https://www.geeksforgeeks.org/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python/
class SketchWriter:
    """
    Generate sketch csv files to train trees.
    """
    FOLDER_NAME: str = "/sketches/"
    SIGNATURE: str = "_sketch.csv"
    SIGNATURE_NEW: str = "_sketch_new.csv"
    COLUMN_NAMES: List[ str ] = [
        fkl_inswitch.SRC_COUNT_STR, fkl_inswitch.SRC_TLS_STR,
        fkl_inswitch.DST_COUNT_STR, fkl_inswitch.DST_TLS_STR,
        fkl_inswitch.LABEL_STR
    ]

    def __init__(
            self, dir: str, pdir: str,
            is_not_balancing: bool = False, ll: int = logging.INFO
    ) -> None:
        """

        @param dir: Directory to re-formatted pkt csv files.
        @param pdir: Directory to original pkt csv files.
        """
        self.data: List = []
        self.labels: List = []
        # Data in the Builder will not be cleared after training.
        self.b: my_dataframe.Builder = my_dataframe.Builder( C = SketchWriter.COLUMN_NAMES )

        self.idx: int = 0
        # gc <- 0 // good pkt count
        self.gc: int = 0
        # bc <- 0 // bad pkt count
        self.bc: int = 0
        self.is_not_balancing: bool = is_not_balancing

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
        if self.is_not_balancing: self.l.info( "Balancing is turned off." );

        self.__counting( df )
        self.__process( df )
        return self.__write( f )

    # Algorithm DATASAMPLING( P )
    # Input. P is input data set to generate a sketch csv file. Assuming we have labled data as our file.
    # Output. Balanced sketch csv file to train a decision tree.
    def __process( self, df: DataFrame ) -> None:
        """
        Extract features from pkts and store the information into the sketch.
        Also Update the sketch with the data sampling applied.
        @param df:
        """
        assert self._c.setLen( my_dataframe.get_row_size( df ) )

        # gdp <- gc / len( P ) // good Drop Percent
        gdp: float = self.gc / my_dataframe.get_row_size( df )
        # bdp <- bc / len( P ) // bad Drop Percent
        bdp: float = self.bc / my_dataframe.get_row_size( df )
        if not self.is_not_balancing:
            self.l.debug( "gdp( bad Drop Percent ): %f, bdp( bad Drop Percent ): %f" % ( gdp, bdp ) )

        # s <- sketch without the limitation threshold.
        s: sketch.Sketch = sketch.Sketch()
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
            assert df.at[ idx, fkl_inswitch.LABEL_STR ] == BAD_LABEL or df.at[ idx, fkl_inswitch.LABEL_STR ] == GOOD_LABEL, df.at[ idx, fkl_inswitch.LABEL_STR ]
            self.__balancing( s.getData( si, di ), df.at[ idx, fkl_inswitch.LABEL_STR ], gdp, bdp )

        assert self._c.isBalanced()
        # return D

    def __write( self, f: str ) -> Tuple[ DataFrame, DataFrame ]:
        """
        Write the sketches with labels to a file.
        @param s: File path where the result sketch file is written.
        """
        # Write to file
        d: str = my_writer.get_dir( f )+ SketchWriter.FOLDER_NAME
        my_writer.make_dir( d )
        fn: str = my_writer.get_filename( f )
        f = d + fn + SketchWriter.SIGNATURE

        if len( self.data ) == 0 or len( self.labels ) == 0:
            self.l.warning( "Sketch: No data written to the file!" )

        # https://www.geeksforgeeks.org/create-a-pandas-dataframe-from-lists/
        df_o: DataFrame = DataFrame( {
            RANGE_STR: self.data,
            fkl_inswitch.LABEL_STR: self.labels
        } )
        self.l.info( "Writing old sketch to:\n" + f )
        df_o.to_csv(
            f, index = False
        )

        df_n: DataFrame = self.b.to_dataframe()
        self.l.info( "Writing new sketch to:\n" + d + fn + SketchWriter.SIGNATURE_NEW )
        df_n.to_csv(
            d + fn + SketchWriter.SIGNATURE_NEW, index = False
        )
        return ( df_o, df_n )

    def __counting( self, df: DataFrame ) -> None:
        """
        Count good pkts and bad pkts.
        @param df:
        """
        # Reset data
        self.data = []
        self.labels = []
        self.gc = 0
        self.bc = 0

        # for every pkt, p, in P
        for ( i, s ) in df.iterrows():
            # do if p is a good one
            if df.at[ i, fkl_inswitch.LABEL_STR ] == GOOD_LABEL:
                # then gc++
                self.gc += 1
            # else bc++
            else:
                assert df.at[ i, fkl_inswitch.LABEL_STR ] == BAD_LABEL
                self.bc += 1

        assert self.gc + self.bc == my_dataframe.get_row_size( df )
        if not self.is_not_balancing:
            self.l.debug( "gc(good count): %d, bc(bad count): %d, tc(total count): %d" % ( self.gc, self.bc, my_dataframe.get_row_size( df ) ) )

    def __balancing( self, D: List[ int ], l: int, gdp: float, bdp: float ) -> None:
        assert 0 <= gdp <= 1
        assert 0 <= bdp <= 1
        assert l == GOOD_LABEL or l == BAD_LABEL

        # ifAddGood <- p is a good one and randDoube() > gdp
        if_add_good: bool = l == GOOD_LABEL and random.random() > gdp
        # ifAddBad <- p is a bad one and randDoube() > bdp
        if_add_bad: bool = l == BAD_LABEL and random.random() > bdp
        # if ifAddGood or ifAddBad
        if self.is_not_balancing or ( if_add_good or if_add_bad ):
            # then d <- [
            #   			[ srcCount in s, srcTL in s, dstCount in s, dstTLS in s ],
            #               label
            #   	    ]
            self.data.append( D )
            self.labels.append( l )

            D_t: List = list( D )
            D_t.append( l )
            self.b.add_row( str( self.idx ), [ str( n ) for n in D_t ] )
            self.idx += 1

            # Record actual good pkts.
            if if_add_good:
                assert l == GOOD_LABEL
                self._c.addGood()
            if if_add_bad:
                assert l == BAD_LABEL
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

        def isBalanced( self ) -> bool:
            self.l.info(
                "R of gc: %0.2f, R of bc: %.2f, gc: %d, bc: %d, tc: %d" % (
                    self.gc / self.tc, self.bc / self.tc, self.gc, self.bc, self.tc
                )
            )
            return True

        def addGood( self ) -> bool:
            self.gc += 1
            return True

        def setLen( self, tc: int ) -> bool:
            self.tc = tc
            return True

        def addBad( self ) -> None:
            self.bc += 1


# https://www.digitalocean.com/community/tutorials/python-unittest-unit-test-example
class _Tester( unittest.TestCase ):
    IS_NOT_BALANCING: bool = True

    def test_bot_lot( self ) -> None:
        dir = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/re-formatted"
        pdir = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/"

        SketchWriter( dir, pdir, _Tester.IS_NOT_BALANCING, 10 ).train()

    def test_ton_lot( self ):
        dir: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/re-formatted"
        pdir: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/"

        SketchWriter( dir, pdir, _Tester.IS_NOT_BALANCING, 10 ).train()

    def test_unsw_nb15( self ):
        dir: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/re-formatted"
        pdir: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/"

        SketchWriter( dir, pdir, _Tester.IS_NOT_BALANCING, 10 ).train()


if __name__ == '__main__':
    unittest.main()
    # unittest.main( argv = [ '' ], defaultTest = [ "_Tester.test_ton_lot" ] )z


