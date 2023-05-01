# -*- coding: utf-8 -*-

import os
import random
import sys
from typing import (
    List, Dict
)
from argparse import (
    ArgumentParser
)
import pandas
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

import Sketch
sys.path.append( "../" )
import csvparaser
sys.path.append( "../com/fengkeyleaf/io/" )
import my_writer
sys.path.append( "../com/fengkeyleaf/utils/lang/" )
import my_math
sys.path.append( "../com/fengkeyleaf/my_pandas/" )
import my_dataframe


RANGE_STR = "range"
GOOD_LABEL = 0
BAD_LABEL = 1 # attack pkt


# https://www.geeksforgeeks.org/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python/
class SketchWriter:
    FOLDER_NAME = "/sketches/"
    SIGNATURE = "_sketch.csv"

    def __init__( self, dir: str, pdir: str ) -> None:
        """

        @param dir: Directory to re-formatted pkt csv files.
        @param pdir: Directory to original pkt csv files.
        """
        self.df: DataFrame = None
        self.data: List = []
        self.labels: List = []
        # gc <- 0 // good pkt count
        self.gc: int = 0
        # bc <- 0 // bad pkt count
        self.bc: int = 0

        for s, d, F in os.walk( dir ):
            for f in F:
                # read in label data
                self.df = pandas.read_csv( os.path.join( s, f ) ) # current dataframe
                # build the sketch
                self.data = []
                self.labels = []
                self.gc = 0
                self.bc = 0

                self.counting()
                self.process()

                # Write to file
                d: str = pdir + SketchWriter.FOLDER_NAME
                my_writer.make_dir( d )
                print( "sketch: " + d + my_writer.get_filename( f ) + SketchWriter.SIGNATURE )
                self.write(
                    d + my_writer.get_filename( f ) + SketchWriter.SIGNATURE
                )

    # Algorithm DATASAMPLING( P )
    # Input. P is input data set to generate a sketch csv file. Assuming we have labled data as our file.
    # Output. Balanced sketch csv file to train a decision tree.
    def process( self ) -> None:
        # gdp <- gc / len( P ) // good Drop Percent
        gdp: float = self.gc / my_dataframe.get_row_size( self.df )
        # bdp <- bc / len( P ) // bad Drop Percent
        bdp: float = self.gc / my_dataframe.get_row_size( self.df )
        # s <- sketch without the limitation threshold.
        s: Sketch.Sketch = Sketch.Sketch()
        # D <- list of sketch data formatted as [ [ srcCount, srcTLS, dstCount, dstTLS ], label ]

        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iterrows.html
        # for every pkt, p, in P
        for ( idx, d ) in self.df.iterrows():
            # Increment the TLS of every tracked ip in s.
            s.incrementTLS()

            si: str = self.df.at[ idx, csvparaser.SRC_ADDR_STR ]
            di: str = self.df.at[ idx, csvparaser.DST_ADDR_STR ]
            # Record p's srcIP and p's dstIP in s.
            s.add_src( si )
            s.add_dst( di )

            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.at.html#pandas.DataFrame.at
            assert self.df.at[ idx, csvparaser.LABEL_STR ] == BAD_LABEL or self.df.at[ idx, csvparaser.LABEL_STR ] == GOOD_LABEL, self.df.at[ idx, csvparaser.LABEL_STR ]
            self.balancing( s.getData( si, di ), self.df.at[ idx, csvparaser.LABEL_STR ], gdp, bdp )

        # return D

    def write( self, s: str ) -> None:
        """
        write the sketches with labels to a file
        @param s: file path.
        """
        # https://www.geeksforgeeks.org/create-a-pandas-dataframe-from-lists/
        pandas.DataFrame( {
            RANGE_STR: self.data,
            csvparaser.LABEL_STR: self.labels
        } ).to_csv(
            s, index = False
        )

    def counting( self ) -> None:
        # for every pkt, p, in P
        for ( i, s ) in self.df.iterrows():
            # do if p is a good one
            if self.df.at[ i, csvparaser.LABEL_STR ] == GOOD_LABEL:
                # then gc++
                self.gc = my_math.add_one( self.gc )
            # else bc++
            else:
                assert self.df.at[ i, csvparaser.LABEL_STR ] == BAD_LABEL
                self.bc = my_math.add_one( self.bc )

    def balancing( self, D: List, l: int, gdp: float, bdp: float ) -> None:
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


if __name__ == '__main__':
    parser:ArgumentParser = ArgumentParser()
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    # parser.add_argument( "-d", "--data", type = str, help="Path to pkt csv file", required = True )
    # parser.add_argument( "-s", "--sketch", type = str, help="Path to sketch csv file", required = True )
    # parser.add_argument( "-dir", "--dir", type = str, help="Directory to pre-processed pkt csv files", required = True )

    args = parser.parse_args()
    # SketchWriter( args.dir )

