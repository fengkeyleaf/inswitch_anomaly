# -*- coding: utf-8 -*-

import unittest
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


# TODO: Default column and index.
class Builder:
    def __init__(
            self, C: List[ str ] = None,
            R: List[ str ] = None, ll: int = logging.INFO
    ) -> None:
        self.C: List[ str ] = [] if C is None else C
        self.R: List[ str ] = [] if R is None else R
        self.D: List[ List[ str ] ] = []

        self.l: logging.Logger = my_logging.get_logger( ll )
        self._c: _Checker = _Checker( self )

    # https://realpython.com/python-kwargs-and-args/
    # TODO: append one element to every row.
    def add_column_name( self, *args: str ):
        for n in args:
            if n is None or n == "":
                self.l.warning( "None name or empty name" )
                continue

            if not ( n in self.C ):
                self.C.append( n )
                continue

            self.l.warning( "Duplicate column name: " + n )

    def add_row_name( self, *args: str ):
        for n in args:
            if n is None or n == "":
                self.l.warning( "None name or empty name" )
                continue

            if not ( n in self.R ):
                self.R.append( n )
                if len( self.R ) > len( self.D ):
                    self.D.append( [] )

                assert len( self.R ) == len( self.D )
                continue

            self.l.warning( "Duplicate row name: " + n )

    def append_element( self, e: str, row_name: str = None, col_name: str = None ) -> Tuple[ int, int ]:
        assert len( self.D[ -1 ] ) + 1 <= len( self.C ), str( len( self.D[ -1 ] ) + 1 ) + " | " + str( len( self.C ) )
        self.D[ -1 ].append( e )

        assert row_name is None or row_name == self.R[ len( self.D ) - 1 ]
        assert col_name is None or col_name == self.C[ len( self.D[ -1 ] ) - 1 ]
        return ( len( self.D ) - 1, len( self.D[ -1 ] ) - 1 )

    def add_row( self, rn: str, R: List[ str ] = None ) -> None:
        if rn in self.R:
            self.l.warning( "Duplicate row name: " + rn )
            return

        if R is None:
            self.l.warning( "Empty row" )
            return

        assert len( R ) == len( self.C ), str( len( R ) ) + " | " + str( len( self.C ) )
        for d in self.D: assert len( R ) == len( d );
        assert self._c.is_full_row()

        self.D.append( R )
        self.add_row_name( rn )

    def reset( self ) -> None:
        self.C = []
        self.R = []
        self.D = []

    def to_csv( self, f: str ) -> None:
        self.l.info( "Saving dataframe to:\n" + f )
        self.to_dataframe().to_csv( f )

    def to_dataframe( self ) -> pandas.DataFrame:
        return pandas.DataFrame(
            numpy.array( self.D ),
            self.R,
            self.C
        )

    def __str__( self ) -> str:
        return str( self.C ) + "\n" + str( self.R ) + "\n" + str( self.D )


class _Checker:
    def __init__( self, b: Builder ):
        self.b: Builder = b

    def is_full_row( self ) -> bool:
        for r in self.b.D:
            assert len( r ) == len( self.b.C ), "Not full row!\n" + str( self.b )

        return True


class _Tester( unittest.TestCase ):
    def test1( self ):
        b: Builder = Builder()
        b.add_column_name( "A", "B", "C" )
        # b.add_row_name( "a", "b", "c" )
        b.add_row( "a", [ "1", "2", "3" ] )
        b.add_row( "b", [ "4", "5", "6" ] )
        b.add_row( "c",[ "7", "8", "9" ] )

        print( b.to_dataframe() )


if __name__ == '__main__':
    unittest.main()
