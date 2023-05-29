# -*- coding: utf-8 -*-

import logging
import math
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

from fengkeyleaf.logging import my_logging
from fengkeyleaf.io import (
    my_files,
    my_writer
)
from fengkeyleaf.my_pandas import my_dataframe
from fengkeyleaf.inswitch_anomaly import (
    mapper,
    sketch_write
)
import fengkeyleaf.inswitch_anomaly as fkl_inswitch


class Mixer:
    """
    Class to mix synthesised pkts.
    """
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
        Mix synthesised pkts into the original data set.
        @param o: All belong to the same network interval, i.e. only one chunk has 0 timestamp.
        @param n: How many synthesised pkts to be aded.
        @return:
        """
        # No synthesised pkts provided.
        if len( self.F ) <= 0: return o;

        # Find out n if not provided.
        if n < 0:
            n = Mixer._get_bads( o )

        self.l.debug( "%d bad pkts in the original data set." % ( n ) )

        c: int = 0
        # TODO: keep un-used pkts.
        while len( self.F ) > 0 and n > 0:
            # https://stackoverflow.com/a/51763708
            df: pandas.DataFrame = None
            fp: str = self.F.pop()
            with open(
                    fp, encoding = my_files.UTF8,
                    errors = my_files.BACK_SLASH_REPLACE
            ) as f:
                assert my_writer.get_extension( fp ).lower() == my_files.CSV
                df = Mixer._label( mapper.Mapper.mapping( pandas.read_csv( f ) ) )

            n -= my_dataframe.get_row_size( df )
            c += my_dataframe.get_row_size( df )

            o = self._pkt_alignment( o, df )

        if len( self.F ) <= 0 < n:
            self.l.warning( "Not enough made-up pkts" )

        self.l.info( "%d made-up pkts added." % ( c ) )
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html#pandas.DataFrame.sort_values
        return o.sort_values( fkl_inswitch.TIMESTAMP_STR )

    # TODO: Identify which group of pkts are more than the other, good or bad?
    @staticmethod
    def _get_bads( o: pandas.DataFrame ) -> int:
        c: int = 0
        for ( i, s ) in o.iterrows():
            if o.loc[ i, fkl_inswitch.LABEL_STR ] == sketch_write.BAD_LABEL:
                c += 1

        return c

    # Only wash out invalid IPs for now.
    @staticmethod
    def _wash( df: pandas.DataFrame ) -> pandas.DataFrame:
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
    def _pkt_alignment( self, o: pandas.DataFrame, m: pandas.DataFrame ) -> pandas.DataFrame:
        ( o, _ ) = self._align( o, self.ort )

        # if m is already reltive to 0
        if Mixer._is_new_group( m ):
            # then Align m retaive to rt, i.e each pkt time += rt.
            # rt = time of the last pkt of m.
            ( m, self.offset ) = Mixer._align( m, self.mrt )

        # d <- concat( o, m )
        # Sort d by pkt timestamps.
        # return ( d, rt )

        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.reset_index.html
        return pandas.concat( [ o, m ] ).reset_index( drop = True )

    @staticmethod
    def _align( df: pandas.DataFrame, rt: float ) -> Tuple[ pandas.DataFrame, float ]:
        """
        Align pkts based on their timestamp.
        THe first pkt in a capture is considered as the one with timestamp 0.00.
        @param df:
        @param rt:
        @return:
        """
        df = df.sort_values( fkl_inswitch.TIMESTAMP_STR )

        # print( df )
        offset: float = -1
        for ( i, s ) in df.iterrows():
            offset = df.loc[ i, fkl_inswitch.TIMESTAMP_STR ]
            df.loc[ i, fkl_inswitch.TIMESTAMP_STR ] -= rt

        # print( df )
        assert offset > -1
        return ( df, offset )

    @staticmethod
    def _is_new_group( m: pandas.DataFrame ) -> bool:
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.head.html#pandas.DataFrame.head
        for ( i, s ) in m.iterrows():
            return math.isclose( m.loc[ i, fkl_inswitch.TIMESTAMP_STR ], 0, rel_tol = 1e-9 )

    @staticmethod
    def _label( df: pandas.DataFrame ) -> pandas.DataFrame:
        """
        Label synthesised good pkts as 0.
        @param df:
        @return:
        """
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.insert.html#pandas.DataFrame.insert
        df.insert( len( df.columns ), fkl_inswitch.LABEL_STR, [ 0 for _ in range( my_dataframe.get_row_size( df ) ) ] )
        return df