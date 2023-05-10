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

from fengkeyleaf.logging import (
    my_logging,
)
from fengkeyleaf.io import my_writer
from fengkeyleaf.inswtich_anomaly import (
    mix_make_ups,
    mapper,
    csvparaser,
)


IP_REG = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"  # raw string


# TODO: too many for s, d, F in os.walk( da ):
# TODO: Parallel computing.
# TODO: Verify pk ids.
class PktProcessor:
    FOLDER_NAME = "/re-formatted/"
    SIGNATURE = "_reformatted.csv"

    def __init__( self, h: str, m: mix_make_ups.Mixer, ll: int = logging.INFO ) -> None:
        """

        @param d: Directory to data set
        @param h: Path to features(headers)
        @param ll: logging level
        """
        # Logging setting
        # https://docs.python.org/3/library/logging.html#logging-levels
        self.l: logging.Logger = my_logging.get_logger( ll )

        self.h: str = h  # header file path
        self.m: mix_make_ups.Mixer = m

    def process( self, f: str ) -> DataFrame:
        df: DataFrame = self.add_header( f )
        df = mapper.Mapper.mapping( df )
        df = self.m.mix( df )
        PktProcessor.spoof_macs( df )
        PktProcessor.renumber( df )
        assert PktProcessor.verify( df, f )

        # Write to file
        self.write( df, f )
        return df

    def add_header( self, f: str ) -> DataFrame:
        # https://www.geeksforgeeks.org/how-to-append-a-new-row-to-an-existing-csv-file/
        # https://www.usepandas.com/csv/append-csv-files

        # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
        # Header is provided.
        if self.h:
            hf: DataFrame = pandas.read_csv( self.h )
            # print( type( hf.columns.values.tolist() ))
            # https://datascienceparichay.com/article/get-column-names-as-list-in-pandas-dataframe/
            cf: DataFrame = pandas.read_csv( f, names = hf.columns.values.tolist() )
            # https://pandas.pydata.org/docs/reference/api/pandas.concat.html
            return pandas.concat( [ hf, cf ] )

        # Default header is provided.
        return pandas.read_csv( f )

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
            si: str = d.at[ i, csvparaser.SRC_ADDR_STR ]
            di: str = d.at[ i, csvparaser.DST_ADDR_STR ]
            id = PktProcessor.create_mac( m, [ si, di ], id, S )

            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html
            assert m[ si ] is not None
            d.loc[ i, csvparaser.SRC_MAC_STR ] = m[ si ]
            assert m[ di ] is not None
            d.loc[ i, csvparaser.DST_MAC_STR ] = m[ di ]


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
            d.loc[ i, csvparaser.ID_STR ] = id
            id += 1

    @staticmethod
    def verify( d: DataFrame, f: str ) -> bool:
        # TODO: verify macs
        for ( i, s ) in d.iterrows():
            # PktProcessor.verify_ip( d )
            assert d.loc[ i, csvparaser.ID_STR ] != "" and d.loc[ i, csvparaser.ID_STR ] is not None
            assert d.loc[ i, csvparaser.LABEL_STR ] == 0 or d.loc[ i, csvparaser.LABEL_STR ] == 1, str( i ) + " | " + f

        return True

    @staticmethod
    def verify_ip( d: DataFrame ) -> bool:
        for ( i, s ) in d.iterrows():
            assert re.search( IP_REG, d.loc[ i , csvparaser.SRC_ADDR_STR ] ), str( i ) + " " +  d.loc[ i , csvparaser.SRC_ADDR_STR ]
            assert re.search( IP_REG, d.loc[ i , csvparaser.DST_ADDR_STR ] ), str( i ) + " " + d.loc[ i , csvparaser.DST_ADDR_STR ]

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


