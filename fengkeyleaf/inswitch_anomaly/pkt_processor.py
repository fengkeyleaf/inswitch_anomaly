# -*- coding: utf-8 -*-

import logging
import math
import re
from typing import (
    Dict, List, Set
)
import pandas
from pandas import (
    DataFrame
)

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
        @Riley McGinn
"""

from fengkeyleaf.logging import my_logging
from fengkeyleaf.io import my_writer
from fengkeyleaf.my_pandas import my_dataframe
import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.inswitch_anomaly import (
    mix_make_ups,
    mapper,
    sketch_write
)


IP_REG = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"  # raw string


# TODO: too many for s, d, F in os.walk( da ):
# TODO: Parallel computing.
# TODO: Verify pk ids.
class PktProcessor:
    """
    Process original pkt data set, like getting rid of unwanted features, adding synthesised good pkts.
    """
    FOLDER_NAME = "/re-formatted/"
    SIGNATURE = "_reformatted.csv"

    def __init__( self, h: str, m: mix_make_ups.Mixer, ll: int = logging.INFO ) -> None:
        """

        @param h: Path to features(headers)
        @param m: mixer to add synthesised good pkts.
        @param ll: logging level
        """
        # Logging setting
        # https://docs.python.org/3/library/logging.html#logging-levels
        self.l: logging.Logger = my_logging.get_logger( ll )
        self.c: PktProcessor._Checker = PktProcessor._Checker( self.l )

        self.h: str = h  # header file path
        self.m: mix_make_ups.Mixer = m

    def process( self, f: str ) -> DataFrame:
        """
        Process a csv pkt file, adding header, mapping features, re-numbering and spoofing macs
        @param f:
        @return:
        """
        df: DataFrame = my_dataframe.add_header( self.h, f )
        df = mapper.Mapper.mapping( df )
        df = self.m.mix( df )
        PktProcessor.spoof_macs( df )
        PktProcessor.renumber( df )
        assert PktProcessor._Checker.verify( df, f )
        assert self.c.statistics( df )

        # Write to file
        self.write( df, f )
        return df

    # TODO: not re-assign
    @staticmethod
    def spoof_macs( d: DataFrame ) -> None:
        """
        Add to input csv to add dest MAC and src MAC
        MACs are consistent with IPs
        @param D:
        """
        # Create a dict to map IPs to MACs
        m: Dict[ str, str ] = { }
        S: Set[ str ] = set()
        id: int = 0

        for ( i, s ) in d.iterrows():
            si: str = d.at[ i, fkl_inswitch.SRC_ADDR_STR ]
            di: str = d.at[ i, fkl_inswitch.DST_ADDR_STR ]
            id = PktProcessor.create_mac( m, [ si, di ], id, S )

            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html
            assert m[ si ] is not None
            d.loc[ i, fkl_inswitch.SRC_MAC_STR ] = m[ si ]
            assert m[ di ] is not None
            d.loc[ i, fkl_inswitch.DST_MAC_STR ] = m[ di ]


    @staticmethod
    def create_mac( m: Dict[ str, str ], I: List[ str ], id: int, s: Set[ str ] ) -> int:
        for i in I:
            if m.get( i ) is None:
                m[ i ] = PktProcessor.create_MAC( id )
                assert m[ i ] not in s
                s.add( m[ i ] )

                id += 1
            else:
                assert m[ i ] is not None and m[ i ] != ""

        return id

    @staticmethod
    def create_MAC( input: int ) -> str:
        return  "{:02d}".format( math.trunc( ( input / 10000000000 ) ) % 100 ) + ':' + \
                "{:02d}".format( math.trunc( ( input / 100000000 ) ) % 100 ) + ':' + \
                "{:02d}".format( math.trunc( ( input / 1000000 ) ) % 100 ) + ':' + \
                "{:02d}".format( math.trunc( ( input / 10000 ) ) % 100 ) + ':' + \
                "{:02d}".format( math.trunc( ( input / 100 ) % 100 ) ) + ':' + \
                "{:02d}".format( input % 100 )

    @staticmethod
    def renumber( d: DataFrame ) -> None:
        id: int = 1
        for ( i, s ) in d.iterrows():
            d.loc[ i, fkl_inswitch.ID_STR ] = id
            id += 1

    class _Checker:
        def __init__( self, l: logging.Logger ):
            self.l: logging.Logger = l

        @staticmethod
        def verify( d: DataFrame, f: str ) -> bool:
            # TODO: verify macs
            for ( i, s ) in d.iterrows():
                # PktProcessor.verify_ip( d )
                assert d.loc[ i, fkl_inswitch.ID_STR ] != "" and d.loc[ i, fkl_inswitch.ID_STR ] is not None
                assert d.loc[ i, fkl_inswitch.LABEL_STR ] == 0 or d.loc[ i, fkl_inswitch.LABEL_STR ] == 1, str( i ) + " | " + f

            return True

        def statistics( self, df ) -> bool:
            gc: int = 0
            bc: int = 0
            tc: int = 0

            for ( i, s ) in df.iterrows():
                if df.loc[ i, fkl_inswitch.LABEL_STR ] == fkl_inswitch.GOOD_LABEL:
                    gc += 1
                elif df.loc[ i, fkl_inswitch.LABEL_STR ] == fkl_inswitch.BAD_LABEL:
                    bc += 1
                else: assert False;
                tc += 1

            self.l.info( "Mixed dataset: gc = %d, bc = %d, tc = %d" % ( gc, bc, tc ) )
            return True

    @staticmethod
    def verify_ip( d: DataFrame ) -> bool:
        for ( i, s ) in d.iterrows():
            assert re.search( IP_REG, d.loc[ i , fkl_inswitch.SRC_ADDR_STR ] ), str( i ) + " " + d.loc[ i , fkl_inswitch.SRC_ADDR_STR ]
            assert re.search( IP_REG, d.loc[ i , fkl_inswitch.DST_ADDR_STR ] ), str( i ) + " " + d.loc[ i , fkl_inswitch.DST_ADDR_STR ]

        return True

    def write( self, df: DataFrame, f: str ) -> None:
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
        # print( len( df ) )
        fp: str = my_writer.get_dir( f )
        fn: str = my_writer.get_filename( f )
        d: str = fp + PktProcessor.FOLDER_NAME
        # https://blog.finxter.com/how-to-save-a-text-file-to-another-folder-in-python/
        my_writer.make_dir( d )

        self.l.info( "pro-process: " + d + fn + PktProcessor.SIGNATURE )
        df.to_csv( d + fn + PktProcessor.SIGNATURE, index = False )


