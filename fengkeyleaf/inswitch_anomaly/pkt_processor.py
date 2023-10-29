# -*- coding: utf-8 -*-

import logging
import math
import random
from typing import Dict, List, Set, Callable
import pandas

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
        @Riley McGinn
"""

from fengkeyleaf.logging import my_logging
from fengkeyleaf.my_pandas import my_dataframe
import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.inswitch_anomaly import mix_make_ups, mapper


# TODO: too many for s, d, F in os.walk( da ):
# TODO: Parallel computing.
# TODO: Verify pk ids.
class PktProcessor:
    """
    Process original pkt data set, like getting rid of unwanted features, adding synthesised good pkts.
    """
    # reformatted file config
    FOLDER_NAME: str = "/re-formatted/"
    SIGNATURE: str = "_reformatted.csv"

    # Balanced original reformatted file config
    BALANCED_FOLDER_NAME: str = "/balanced_reformatted/"
    BALANCED_SIGNATURE: str = "_balanced_reformatted.csv"

    def __init__(
            self, h: str, m: mix_make_ups.Mixer,
            fn: Callable = None, ll: int = logging.INFO
    ) -> None:
        """

        @param h: Path to features(headers)
        @param m: mixer to add synthesised good pkts.
        @param ll: logging level
        """
        # Logging setting
        # https://docs.python.org/3/library/logging.html#logging-levels
        self.l: logging.Logger = my_logging.get_logger( ll )
        self._cm: PktProcessor._CheckerMixer = PktProcessor._CheckerMixer( self.l )
        self._cb: PktProcessor._CheckerBalancing = self._CheckerBalancing( self.l )

        # Pkt dataset setting
        self.h: str = h  # header file path
        self.m: mix_make_ups.Mixer = m

        # Filtering setting
        self.fn: Callable = fn

        # Data sampling/balancing setting.
        self._is_balancing: bool = True
        # gc <- 0 // good pkt count
        self.gc: int = 0
        # bc <- 0 // bad pkt count
        self.bc: int = 0

    def process( self, f: str ) -> pandas.DataFrame:
        """
        Process a csv pkt file, adding header, mapping features, re-numbering and spoofing macs
        @param f: File path to the original pkt csv file.
        @return:
        """
        # Add a feature header.
        df: pandas.DataFrame = my_dataframe.add_header( self.h, f )
        # Mapping raw features to our features.
        df = mapper.Mapper.mapping( df )
        # Mix with synthesised good pkts if provided.
        df = self.m.mix( df )
        assert self._cm.statistics( df )

        # Spoof macs and renumber.
        PktProcessor.spoof_macs( df )
        # TODO: id is inconsistent.
        PktProcessor.renumber( df )
        assert PktProcessor._Checker.verify( df, f )

        # Filtering.
        if self.fn is not None:
            self.l.info( "Pkt filter is enabled." )
            df = self.fn( df )

        # Write to file
        return self.write(
            # Original reformatted data.
            df,
            # Data sampling/balancing
            self._balancing( df ),
            f
        )

    # TODO: not re-assign
    @staticmethod
    def spoof_macs( d: pandas.DataFrame ) -> None:
        """
        Add to input csv to add dest MAC and src MAC
        MACs are consistent with IPs
        @param d:
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
    def renumber( d: pandas.DataFrame ) -> None:
        id: int = 1
        for ( i, s ) in d.iterrows():
            d.loc[ i, fkl_inswitch.ID_STR ] = id
            id += 1

    def write( self, df_o: pandas.DataFrame, df_b: pandas.DataFrame, f: str ) -> pandas.DataFrame:
        fp: str = fkl_inswitch.get_output_file_path(
            f, PktProcessor.FOLDER_NAME, PktProcessor.SIGNATURE
        )
        self.l.info( "Pro-process: " + fp )
        df_o.to_csv( fp, index = False )

        if self._is_balancing:
            fp: str = fkl_inswitch.get_output_file_path(
                f, PktProcessor.BALANCED_FOLDER_NAME, PktProcessor.BALANCED_SIGNATURE
            )
            self.l.info( "Pro-process balanced: " + fp )
            df_b.to_csv( fp, index = False )
            return df_b

        return df_o

    def _counting( self, df: pandas.DataFrame ) -> None:
        """
        Count good pkts and bad pkts.
        @param df:
        """
        # Reset
        self.gc = 0
        self.bc = 0

        # for every pkt, p, in P
        for ( i, s ) in df.iterrows():
            # do if p is a good one
            if df.at[ i, fkl_inswitch.LABEL_STR ] == fkl_inswitch.GOOD_LABEL:
                # then gc++
                self.gc += 1
                continue

            # else bc++
            assert df.at[ i, fkl_inswitch.LABEL_STR ] == fkl_inswitch.BAD_LABEL
            self.bc += 1

        assert self.gc + self.bc == my_dataframe.get_row_size( df )
        if self._is_balancing:
            self.l.debug( "gc(good count): %d, bc(bad count): %d, tc(total count): %d" % ( self.gc, self.bc, my_dataframe.get_row_size( df ) ) )

    # Algorithm DATASAMPLING( P )
    def _balancing( self, df: pandas.DataFrame ) -> pandas.DataFrame:
        """
        Data sampling/balancing.
        @param df:
        @return: Original pkt dataframe if data balancing is off, otherwise balanced pkt dataframe.
        """
        if not self._is_balancing: return df;

        assert self._cb.setLen( my_dataframe.get_row_size( df ) )

        self.l.info( "Balancing is turned on in PktProcessor." )
        self._counting( df )

        # gdp <- gc / len( P ) // good Drop Percent
        gdp: float = self.gc / my_dataframe.get_row_size( df )
        # bdp <- bc / len( P ) // bad Drop Percent
        bdp: float = self.bc / my_dataframe.get_row_size( df )
        self.l.debug( "gdp( bad Drop Percent ): %f, bdp( bad Drop Percent ): %f" % (gdp, bdp) )

        return self._selecting( df, gdp, bdp )

    def _is_added( self, ifg: bool, ifb: bool ) -> bool:
        # Add a pkt if data balancing is off or
        return ( not self._is_balancing or
                 # add one from a probabilistic perspective
                 ( ifg or ifb ) )

    def _selecting(
            self, df: pandas.DataFrame, gdp: float, bdp: float
    ) -> pandas.DataFrame:
        """
        Data balancing process.
        @param df:
        @param gdp: Good pkt probability.
        @param bdp: Bad pkt probability.
        @return: Balanced pkt dataframe.
        """
        assert 0 <= gdp <= 1
        assert 0 <= bdp <= 1

        I: List[ int ] = []
        for ( idx, _ ) in df.iterrows():
            l: int = df.at[ idx, fkl_inswitch.LABEL_STR ]
            assert l == fkl_inswitch.GOOD_LABEL or l == fkl_inswitch.BAD_LABEL

            # ifAddGood <- p is a good one and randDoube() > gdp
            if_add_good: bool = l == fkl_inswitch.GOOD_LABEL and random.random() > gdp
            # ifAddBad <- p is a bad one and randDoube() > bdp
            if_add_bad: bool = l == fkl_inswitch.BAD_LABEL and random.random() > bdp

            # if ifAddGood or ifAddBad
            # Add a pkt
            if self._is_added( if_add_good, if_add_bad ):
                assert self._cb.count( l, if_add_good, if_add_bad )
                continue

            # Not add, record its index and then drop it later.
            I.append( idx )

        assert self._cb.is_balanced()
        return df.drop( I )

    class _Checker:
        @staticmethod
        def verify( d: pandas.DataFrame, f: str ) -> bool:
            # TODO: verify macs
            for (i, s) in d.iterrows():
                # PktProcessor.verify_ip( d )
                assert d.loc[ i, fkl_inswitch.ID_STR ] != "" and d.loc[ i, fkl_inswitch.ID_STR ] is not None
                assert d.loc[ i, fkl_inswitch.LABEL_STR ] == 0 or d.loc[ i, fkl_inswitch.LABEL_STR ] == 1, str(
                    i ) + " | " + f

            return True

    class _CheckerMixer:
        def __init__( self, l: logging.Logger ):
            self.l: logging.Logger = l

        def statistics( self, df ) -> bool:
            gc: int = 0
            bc: int = 0
            tc: int = 0

            for ( i, s ) in df.iterrows():
                if df.loc[ i, fkl_inswitch.LABEL_STR ] == fkl_inswitch.GOOD_LABEL:
                    gc += 1
                elif df.loc[ i, fkl_inswitch.LABEL_STR ] == fkl_inswitch.BAD_LABEL:
                    bc += 1
                else: assert False, df.loc[ i, fkl_inswitch.LABEL_STR ];
                tc += 1

            self.l.info( "Mixed dataset: gc = %d, bc = %d, tc = %d" % ( gc, bc, tc ) )
            return True

    class _CheckerBalancing:
        def __init__( self, l: logging.Logger ):
            self.tc: int = 0 # total pkt count
            self.gc: int = 0 # actual good count
            self.bc: int = 0

            self.l = l

        def is_balanced( self ) -> bool:
            # Balancing info
            self.l.info(
                "R of gc: %0.2f, R of bc: %.2f, gc: %d, bc: %d, tc: %d" % (
                    self.gc / self.tc, self.bc / self.tc, self.gc, self.bc, self.tc
                )
            )
            return True

        def _addGood( self ) -> bool:
            self.gc += 1
            return True

        def _addBad( self ) -> None:
            self.bc += 1

        def setLen( self, tc: int ) -> bool:
            self.tc = tc
            return True

        def count( self, l: int, is_good: bool, is_bad: bool ) -> bool:
            # Record actual good pkts and bad pkts, i.e. count their numbers.
            if is_good:
                assert l == fkl_inswitch.GOOD_LABEL
                self._addGood()
            if is_bad:
                assert l == fkl_inswitch.BAD_LABEL
                self._addBad()

            return True
