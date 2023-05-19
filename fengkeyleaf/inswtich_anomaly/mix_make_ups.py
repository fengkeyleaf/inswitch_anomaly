# -*- coding: utf-8 -*-

import logging
import math
import os
import re
from typing import (
    List, Tuple
)

import pandas

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import (
    my_logging,
)
from fengkeyleaf.io import (
    my_files
)
from fengkeyleaf.my_pandas import (
    my_dataframe
)
from fengkeyleaf.inswtich_anomaly import (
    mapper,
    csvparaser,
    sketch_write
)


class Mixer:
    def __init__( self, dir_m: str, ort: float, ll: int = logging.INFO ) -> None:
        self.l: logging.Logger = my_logging.get_logger( ll )

        self.F: List[ str ] = my_files.get_files_in_dir( dir_m )
        if dir_m is None or len( self.F ) == 0:
            self.l.debug( "No made-up data sets provided." )

        assert ort >= 0
        self.ort: float = ort
        self.mrt: float = 0
        self.offset = 0

    # https://pandas.pydata.org/docs/reference/api/pandas.concat.html
    def mix( self, o: pandas.DataFrame, n: int = -1 ) -> pandas.DataFrame:
        """

        @param o: All belong to the same network interval, i.e. only one chunk has 0 timestamp.
        @param n:
        @return:
        """
        if len( self.F ) <= 0: return o;

        if n < 0:
            n = Mixer.get_bads( o )

        self.l.debug( "%d bad pkts in the original data set." % ( n ) )

        c: int = 0
        # TODO: keep un-used pkts.
        while len( self.F ) > 0 and n > 0:
            # https://stackoverflow.com/a/51763708
            df: pandas.DataFrame = None
            with open( self.F.pop(), encoding = "utf8", errors = 'backslashreplace' ) as f:
                df = Mixer.label( mapper.Mapper.mapping( pandas.read_csv( f ) ) )

            n -= my_dataframe.get_row_size( df )
            c += my_dataframe.get_row_size( df )

            o = self.pkt_alignment( o, df )

        if len( self.F ) <= 0 < n:
            self.l.warning( "Not enough made-up pkts" )

        self.l.info( "%d made-up pkts added." % ( c ) )
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html#pandas.DataFrame.sort_values
        return o.sort_values( csvparaser.TIMESTAMP_STR )

    # TODO: Identify which group of pkts are more than the other, good or bad?
    @staticmethod
    def get_bads( o: pandas.DataFrame ) -> int:
        c: int = 0
        for ( i, s ) in o.iterrows():
            if o.loc[ i, csvparaser.LABEL_STR ] == sketch_write.BAD_LABEL:
                c += 1

        return c

    # Only wash out invalid IPs for now.
    @staticmethod
    def wash( df: pandas.DataFrame ) -> pandas.DataFrame:
        I: List[ int ] = []
        # for ( i, s ) in df.iterrows():
            # if re.search( pkt_processor.IP_REG, df.loc[ i, csvparaser.SRC_ADDR_STR ] ) is None or \
            #         re.search( pkt_processor.IP_REG, df.loc[ i, csvparaser.DST_ADDR_STR ] ) is None:
                # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html
                # I.append( i )

        return df.drop( I )

    # Algorithm PKTALIGNMENT( o, m, rt = 0 )
    # Input. Original data set, o, made-up data sets, m.
    # Output. Data set, d, combining o and M sorted by pkt timestamps, and relative pkt time, rt.
    def pkt_alignment( self, o: pandas.DataFrame, m: pandas.DataFrame ) -> pandas.DataFrame:
        ( o, _ ) = self.align( o, self.ort )

        # if m is already reltive to 0
        if Mixer.is_new_group( m ):
            # then Align m retaive to rt, i.e each pkt time += rt.
            # rt = time of the last pkt of m.
            ( m, self.offset ) = Mixer.align( m, self.mrt )

        # d <- concat( o, m )
        # Sort d by pkt timestamps.
        # return ( d, rt )

        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html
        return pandas.concat( [ o, m ] ).reset_index( drop = True )

    @staticmethod
    def align( df: pandas.DataFrame, rt: float ) -> Tuple[ pandas.DataFrame, float ]:
        df = df.sort_values( csvparaser.TIMESTAMP_STR )

        # print( df )
        offset: float = -1
        for ( i, s ) in df.iterrows():
            offset = df.loc[ i, csvparaser.TIMESTAMP_STR ]
            df.loc[ i, csvparaser.TIMESTAMP_STR ] -= rt

        # print( df )
        assert offset > -1
        return ( df, offset )

    @staticmethod
    def is_new_group( m: pandas.DataFrame ) -> bool:
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.head.html#pandas.DataFrame.head
        for ( i, s ) in m.iterrows():
            return math.isclose( m.loc[ i, csvparaser.TIMESTAMP_STR ], 0, rel_tol = 1e-9 )

    @staticmethod
    def label( df: pandas.DataFrame ) -> pandas.DataFrame:
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.insert.html#pandas.DataFrame.insert
        df.insert( len( df.columns ), csvparaser.LABEL_STR, [ 0 for _ in range( my_dataframe.get_row_size( df ) ) ] )
        return df