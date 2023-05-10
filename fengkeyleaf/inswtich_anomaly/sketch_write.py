# -*- coding: utf-8 -*-

import logging
import random
from argparse import (
    ArgumentParser
)
from typing import (
    List
)

from pandas import (
    DataFrame
)

"""
file:
description: file to do sketch building and write results to a csv file
language: python3 3.11.3
author: @sean bergen,
        @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import (
    my_logging,
)
from fengkeyleaf.my_pandas import (
    my_dataframe
)
from fengkeyleaf.io import my_writer

from fengkeyleaf.inswtich_anomaly import (
    csvparaser,
    sketch
)


RANGE_STR = "range"
GOOD_LABEL = 0
BAD_LABEL = 1 # attack pkt


# https://www.geeksforgeeks.org/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python/
class SketchWriter:
    FOLDER_NAME = "/sketches/"
    SIGNATURE = "_sketch.csv"

    def __init__( self, dir: str, pdir: str, ll: int = logging.INFO ) -> None:
        """

        @param dir: Directory to re-formatted pkt csv files.
        @param pdir: Directory to original pkt csv files.
        """
        self.l: logging.Logger = my_logging.get_logger( ll )

        self.data: List = []
        self.labels: List = []
        # gc <- 0 // good pkt count
        self.gc: int = 0
        # bc <- 0 // bad pkt count
        self.bc: int = 0

        self.c: SketchWriter.__Checker = self.__Checker( self.l )

    def process( self, df: DataFrame, f: str ) -> DataFrame:
        self.__counting( df )
        self.__process( df )
        return self.__write( f )

    # Algorithm DATASAMPLING( P )
    # Input. P is input data set to generate a sketch csv file. Assuming we have labled data as our file.
    # Output. Balanced sketch csv file to train a decision tree.
    def __process( self, df: DataFrame ) -> None:
        assert self.c.setLen( my_dataframe.get_row_size( df ) )

        # gdp <- gc / len( P ) // good Drop Percent
        gdp: float = self.gc / my_dataframe.get_row_size( df )
        # bdp <- bc / len( P ) // bad Drop Percent
        bdp: float = self.bc / my_dataframe.get_row_size( df )
        self.l.debug( "gdp: %f, bdp: %f" % ( gdp, bdp ) )
        # s <- sketch without the limitation threshold.
        s: sketch.Sketch = sketch.Sketch()
        # D <- list of sketch data formatted as [ [ srcCount, srcTLS, dstCount, dstTLS ], label ]

        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iterrows.html
        # for every pkt, p, in P
        for ( idx, d ) in df.iterrows():
            # Increment the TLS of every tracked ip in s.
            s.incrementTLS()

            si: str = df.at[ idx, csvparaser.SRC_ADDR_STR ]
            di: str = df.at[ idx, csvparaser.DST_ADDR_STR ]
            # Record p's srcIP and p's dstIP in s.
            s.add_src( si )
            s.add_dst( di )

            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.at.html#pandas.DataFrame.at
            assert df.at[ idx, csvparaser.LABEL_STR ] == BAD_LABEL or df.at[ idx, csvparaser.LABEL_STR ] == GOOD_LABEL, df.at[ idx, csvparaser.LABEL_STR ]
            self.__balancing( s.getData( si, di ), df.at[ idx, csvparaser.LABEL_STR ], gdp, bdp )

        assert self.c.isBalanced()
        # return D

    def __write( self, f: str ) -> DataFrame:
        """
        write the sketches with labels to a file
        @param s: file path.
        """
        # Write to file
        d: str = my_writer.get_dir( f )+ SketchWriter.FOLDER_NAME
        my_writer.make_dir( d )
        f = d + my_writer.get_filename( f ) + SketchWriter.SIGNATURE
        self.l.info( "sketch: " + f )

        if len( self.data ) == 0 or len( self.labels ) == 0:
            self.l.warning( "Sketch: No data written to the file!" )

        # https://www.geeksforgeeks.org/create-a-pandas-dataframe-from-lists/
        df: DataFrame = DataFrame( {
            RANGE_STR: self.data,
            csvparaser.LABEL_STR: self.labels
        } )
        df.to_csv(
            f, index = False
        )
        return df

    def __counting( self, df: DataFrame ) -> None:
        self.data = []
        self.labels = []
        self.gc = 0
        self.bc = 0

        # for every pkt, p, in P
        for ( i, s ) in df.iterrows():
            # do if p is a good one
            if df.at[ i, csvparaser.LABEL_STR ] == GOOD_LABEL:
                # then gc++
                self.gc += 1
            # else bc++
            else:
                assert df.at[ i, csvparaser.LABEL_STR ] == BAD_LABEL
                self.bc += 1

        assert self.gc + self.bc == my_dataframe.get_row_size( df )
        self.l.debug( "gc: %d, bc: %d, tc: %d" % ( self.gc, self.bc, my_dataframe.get_row_size( df ) ) )

    def __balancing( self, D: List, l: int, gdp: float, bdp: float ) -> None:
        assert 0 <= gdp <= 1
        assert 0 <= bdp <= 1
        assert l == GOOD_LABEL or l == BAD_LABEL

        # ifAddGood <- p is a good one and randDoube() > gdp
        if_add_good: bool = l == GOOD_LABEL and random.random() > gdp
        # ifAddBad <- p is a bad one and randDoube() > bdp
        if_add_bad: bool = l == BAD_LABEL and random.random() > bdp
        # if ifAddGood or ifAddBad
        if if_add_good or if_add_bad:
            # then d <- [
            #   			[ srcCount in s, srcTL in s, dstCount in s, dstTLS in s ],
            #               label
            #   	    ]
            self.data.append( D )
            self.labels.append( l )

            # Record actual good pkts.
            if if_add_good: self.c.addGood();
            if if_add_bad: self.c.addBad();

    class __Checker:
        def __init__( self, l: logging.Logger ):
            self.tc: int = 0 # total pkt count
            self.gc: int = 0 # actual good count
            self.bc: int = 0

            self.l = l

        def isBalanced( self ) -> bool:
            self.l.info( "R of gc: %0.2f, R of bc: %.2f, gc: %d, bc: %d, tc: %d" % ( self.gc / self.tc, self.bc / self.tc, self.gc, self.bc, self.tc ) )
            return True

        def addGood( self ) -> bool:
            self.gc += 1
            return True

        def setLen( self, tc: int ) -> bool:
            self.tc = tc
            return True

        def addBad( self ) -> None:
            self.bc += 1


if __name__ == '__main__':
    parser:ArgumentParser = ArgumentParser()
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    # parser.add_argument( "-d", "--data", type = str, help="Path to pkt csv file", required = True )
    # parser.add_argument( "-s", "--sketch", type = str, help="Path to sketch csv file", required = True )
    # parser.add_argument( "-dir", "--dir", type = str, help="Directory to pre-processed pkt csv files", required = True )

    args = parser.parse_args()
    # SketchWriter( args.dir )


