# -*- coding: utf-8 -*-
import numpy
import pandas
from typing import List, Tuple
import logging

"""
file: .py
description:
language: python3 3.11.3
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging

# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.size.html#pandas.DataFrame.size
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.columns.html#pandas.DataFrame.columns
def get_row_size( d: pandas.DataFrame ) -> int:
    """
    Get the row size for the give DataFrame.
    @param d:
    @return:
    """
    assert int( d.size / d.columns.size ) == d.size // d.columns.size
    return d.size // d.columns.size


def add_header( h: str, f: str ) -> pandas.DataFrame:
    """
    Add a header to a csv if there isn't a one.
    @param h: File path to the header.
    @param f: File path to the csv file.
    @return:
    """
    # https://www.geeksforgeeks.org/how-to-append-a-new-row-to-an-existing-csv-file/
    # https://www.usepandas.com/csv/append-csv-files

    # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    # Header is provided.
    if h is not None and h != "":
        hf: pandas.DataFrame = pandas.read_csv( h )
        # print( type( hf.columns.values.tolist() ))
        # https://datascienceparichay.com/article/get-column-names-as-list-in-pandas-dataframe/
        cf: pandas.DataFrame = pandas.read_csv( f, names = hf.columns.values.tolist() )
        # https://pandas.pydata.org/docs/reference/api/pandas.concat.html
        return pandas.concat( [ hf, cf ] )

    # Default header is provided.
    return pandas.read_csv( f )


def get_feature_content( df: pandas.DataFrame, l: str, F: List[ str ] = None ) -> pandas.DataFrame:
    assert l is not None and l != "", l
    assert ( F is None or len( F ) <= 0 ) or not ( l in F )

    if F is None or len( F ) <= 0:
        F = df.columns.values.tolist()
        F.remove( l )

    return df[ F ]


class Generator:
    def __init__( self, ll: int = logging.INFO ):
        self.l: logging.Logger = my_logging.get_logger( ll )

        self.C: List[ str ] = []
        self.R: List[ str ] = []
        self.D: List[ List[ str ] ] = []

    def add_column_name( self, n: str ):
        if  n in self.C:
            self.l.warning( "Duplicate column name: " + n )
            return
        self.C.append( n )

    def add_row_name( self, n: str ):
        if n in self.R:
            self.l.warning( "Duplicate row name: " + n )
            return

        self.R.append( n )
        self.D.append( [] )

        assert len( self.R ) == len( self.D )

    def append_element( self, e: str, row_name: str == None, col_name: str = None ) -> Tuple[ int, int ]:
        assert len( self.D[ -1 ] ) + 1 <= len( self.C ), str( len( self.D[ -1 ] ) + 1 ) + " | " + str( len( self.C ) )
        self.D[ -1 ].append( e )

        assert row_name is None or row_name == self.R[ len( self.D ) - 1 ]
        assert col_name is None or col_name == self.C[ len( self.D[ -1 ] ) - 1 ]
        return ( len( self.D ) - 1, len( self.D[ -1 ] ) - 1 )

    def reset( self ):
        self.C = []
        self.R = []
        self.D = []

    def to_csv( self, f: str ):
        self.l.info( "Saving dataframe to:\n" + f )
        pandas.DataFrame(
            numpy.array( self.D ),
            self.R,
            self.C
        ).to_csv( f )

