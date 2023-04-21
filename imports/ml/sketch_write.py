# -*- coding: utf-8 -*-

"""
file:
description: file to do sketch building and write results to a csv file
language: python3 3.11.3
author: @sean bergen,
        @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""
import os
import sys
import random as rd
from typing import (
    List
)
from argparse import (
    ArgumentParser
)
import pandas
from pandas import (
    DataFrame
)

sys.path.append( "../" )
import csvparaser
sys.path.append( "../com/fengkeyleaf/io/" )
import my_writer

"""
functions to update the sketch
"""


# lowest count, the simplest one
def lowest_count( IP, sketch ):
    in_sketch = False
    for i in range( len( sketch ) ):
        if IP in sketch[ i ]:
            sketch[ i ][ 1 ] = sketch[ i ][ 1 ] + 1
            in_sketch = True
            # reset tls
            sketch[ i ][ 2 ] = 0
    # if ip was not in sketch, find smallest count to
    # replace
    if in_sketch == False:
        min_n = sketch[ 0 ][ 1 ]
        min_i = 0
        for i in range( len( sketch ) ):
            # replace empty indices
            if sketch[ i ][ 1 ] == None:
                min_i = i
                break
            # we also check if there are any we haven't
            # seen in a long time and replace them over
            # low counts
            if sketch[ i ][ 2 ] == 0:
                min_i = i
                min_n = -1
            # if no empty indices go find small
            # count among vals
            if sketch[ i ][ 1 ] < min_n:
                min_n = sketch[ i ][ 1 ]
                min_i = i
        sketch[ min_i ] = [ IP, 1, 0 ]
    # increment all other TLS
    for i in range( len( sketch ) ):
        if sketch[ i ][ 2 ] == None:
            pass
        else:
            sketch[ i ][ 2 ] = sketch[ i ][ 2 ] + 1


# highest tls, the second-simplest one
def highest_tls( IP, sketch ):
    in_sketch = False
    for i in range( len( sketch ) ):
        if IP in sketch[ i ]:
            sketch[ i ][ 1 ] = sketch[ i ][ 1 ] + 1
            in_sketch = True
            # reset tls
            sketch[ i ][ 2 ] = 0
    # if ip was not in sketch, find largest tls to (time last seen)
    # replace
    if in_sketch == False:
        min_n = sketch[ 0 ][ 2 ]
        min_i = 0
        for i in range( len( sketch ) ):
            # replace empty indices
            if sketch[ i ][ 2 ] == None:
                min_i = i
                break
            # if no empty indices go find large
            # tls among vals
            if sketch[ i ][ 2 ] > min_n:
                min_n = sketch[ i ][ 2 ]
                min_i = i
        sketch[ min_i ] = [ IP, 1, 0 ]
    # increment all other TLS
    for i in range( len( sketch ) ):
        if sketch[ i ][ 2 ] == None:
            pass
        else:
            sketch[ i ][ 2 ] = sketch[ i ][ 2 ] + 1


# don't replace, the third-simplest one (replace if empty)
def no_replace( IP, sketch ):
    in_sketch = False
    for i in range( len( sketch ) ):
        if IP in sketch[ i ]:
            sketch[ i ][ 1 ] = sketch[ i ][ 1 ] + 1
            # reset tls
            sketch[ i ][ 2 ] = 0
            in_sketch = True
    if in_sketch == False:
        for i in range( len( sketch ) ):
            # replace empty indices
            if sketch[ i ][ 1 ] == None:
                sketch[ i ] = [ IP, 1, 0 ]
                break
    # increment all other TLS
    for i in range( len( sketch ) ):
        if sketch[ i ][ 2 ] == None:
            pass
        else:
            sketch[ i ][ 2 ] = sketch[ i ][ 2 ] + 1


# replace indice with the lowest value for count mult with ttl
def low_score( IP, sketch ):
    in_sketch = False
    for i in range( len( sketch ) ):
        if IP in sketch[ i ]:
            sketch[ i ][ 1 ] = sketch[ i ][ 1 ] + 1
            in_sketch = True
            # reset tls
            sketch[ i ][ 2 ] = 0
    # if ip was not in sketch, find smallest count to
    # replace
    if in_sketch == False:
        if sketch[ i ][ 1 ] == None:
            min_n = 0
        else:
            min_n = sketch[ 0 ][ 1 ] * (1000 - sketch[ 0 ][ 2 ])
        min_i = 0
        for i in range( len( sketch ) ):
            # replace empty indices
            if sketch[ i ][ 1 ] == None:
                min_i = i
                break
            # if no empty indices go find small
            # count among vals
            if sketch[ i ][ 1 ] * sketch[ i ][ 2 ] < min_n:
                min_n = sketch[ i ][ 1 ] * sketch[ i ][ 2 ]
                min_i = i
        sketch[ min_i ] = [ IP, 1, 0 ]
    # increment all other TLS
    for i in range( len( sketch ) ):
        if sketch[ i ][ 2 ] == None:
            pass
        else:
            sketch[ i ][ 2 ] = sketch[ i ][ 2 ] + 1


def update_sketch( si: str, di: str, sketch: List, r: int ) -> None:
    """
    sketch is size 2 list containing sources sketch and dest sketch
    row is the current packet we are looking at, [1] = src.ip, [2] = dst.ip
    r is a random integer between [0,3] (both inclusive) and determines
    the policy we update the sketch with
    @param si: src ip
    @param di: dst ip
    @param sketch:
    @param r:
    """
    if r == 0:
        lowest_count( si, sketch[ 0 ] )
        lowest_count( di, sketch[ 1 ] )
    elif r == 1:
        highest_tls( si, sketch[ 0 ] )
        highest_tls( di, sketch[ 1 ] )
    elif r == 2:
        no_replace( si, sketch[ 0 ] )
        no_replace( di, sketch[ 1 ] )
    elif r == 3:
        low_score( si, sketch[ 0 ] )
        low_score( di, sketch[ 1 ] )
    else:
        assert False


RANGE_STR = "range"

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

        for s, d, F in os.walk( dir ):
            for f in F:
                # read in label data
                self.df = pandas.read_csv( os.path.join( s, f ) )
                # build the sketch
                self.data = []
                self.labels = []

                self.process()

                d: str = pdir + SketchWriter.FOLDER_NAME
                my_writer.make_dir( d )
                print( "sketch: " + d + my_writer.get_filename( f ) + SketchWriter.SIGNATURE )
                self.write(
                    d + my_writer.get_filename( f ) + SketchWriter.SIGNATURE
                )

    def process( self ) -> None:
        # counter to reset the sketch every 1000 packets
        counter: int = 0
        sketch: List = [ [ [ None, None, None ] ] * 8, [ [ None, None, None ] ] * 8 ]
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iterrows.html
        for ( idx, d ) in self.df.iterrows():
            # reset the sketch every 1000 packets
            if counter % 100 == 0:
                # just to see
                # print( sketch )
                pass
                # sketch = [[[None,None,None]]*8,[[None,None,None]]*8]
            counter = counter + 1

            # assuming we have labled data as our file

            # current policies:
            #    lowest_count
            #    lowest_ttl
            #    no_replace
            #    low_score
            r: int = rd.randrange( 4 )

            # we pass the data into the tree classifier as follows:
            #       0,1000 if not in sketch, ct,tls if in
            tmp: List = [ ]
            ind: int = -1

            si: str = self.df.at[ idx, csvparaser.SRC_ADDR_STR ]
            di: str = self.df.at[ idx, csvparaser.DST_ADDR_STR ]
            for i in range( len( sketch[ 0 ] ) ):
                if si == sketch[ 0 ][ i ][ 0 ]:
                    ind = i
            if ind >= 0:
                tmp = [ sketch[ 0 ][ ind ][ 1 ], sketch[ 0 ][ ind ][ 2 ] ]
                # tmp = [sketch[0][ind][1],sketch[0][ind][2]]
            else:
                tmp = [ 0, 1000 ]
                # tmp = [0,1000]
            ind = -1
            for i in range( len( sketch[ 1 ] ) ):
                if di == sketch[ 1 ][ i ][ 0 ]:
                    ind = i
            if ind >= 0:
                tmp.append( sketch[ 1 ][ ind ][ 1 ] )
                tmp.append( sketch[ 1 ][ ind ][ 2 ] )
            else:
                tmp.append( 0 )
                tmp.append( 1000 )
            # update sketch afterwards
            update_sketch( si, di, sketch, r )

            self.data.append( list( tmp ) )
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.at.html#pandas.DataFrame.at
            assert self.df.at[ idx, csvparaser.LABEL_STR ] == 1 or self.df.at[ idx, csvparaser.LABEL_STR ] == 0, self.df.at[ idx, csvparaser.LABEL_STR ]
            self.labels.append( self.df.at[ idx, csvparaser.LABEL_STR ] )

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


if __name__ == '__main__':
    parser:ArgumentParser = ArgumentParser()
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    # parser.add_argument( "-d", "--data", type = str, help="Path to pkt csv file", required = True )
    # parser.add_argument( "-s", "--sketch", type = str, help="Path to sketch csv file", required = True )
    # parser.add_argument( "-dir", "--dir", type = str, help="Directory to pre-processed pkt csv files", required = True )

    args = parser.parse_args()
    # SketchWriter( args.dir )

