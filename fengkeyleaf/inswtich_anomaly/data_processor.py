# -*- coding: utf-8 -*-

import logging
import os
import sys
from typing import List
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
"""

from fengkeyleaf.logging import my_logging
from fengkeyleaf.inswtich_anomaly import (
    csvparaser,
    mapper,
    mix_make_ups,
    pkt_processor,
    sketch_write,
    tree
)

# parent-directory..
#     | --> original_data..
#     | --> mixed_data..
#     | --> preprocessed_data..
#     | --> sketches..
#     | --> trees..
#     | --> header ( optional )

# TODO: Mix different group of data sets.
class DataProcessor:
    def __init__( self, da: str, h: str, dm: str, ll: int = logging.INFO ) -> None:
        """

        @param d: Directory to data set
        @param h: Path to features(headers)
        @param ll: logging level
        """
        # Logging setting
        # https://docs.python.org/3/library/logging.html#logging-levels
        self.l: logging.Logger = my_logging.get_logger( ll )
        self.l.debug( "da: " + str( da ) )
        self.l.debug( "h: " + str( h ) )
        self.l.debug( "dm: " + str( dm ) )

        self.da: str = da
        assert da is not None
        self.pkt_processor: pkt_processor.PktProcessor = pkt_processor.PktProcessor(
            h,
            mix_make_ups.Mixer( dm, self.__get_original_relative_time( da, h ), ll ),
            ll
        )
        self.sketch_processor: sketch_write.SketchWriter = sketch_write.SketchWriter(
            da + pkt_processor.PktProcessor.FOLDER_NAME,
            da,
            ll
        )
        self.tree: tree.Tree = tree.Tree(
            da + sketch_write.SketchWriter.FOLDER_NAME,
            da,
            ll
        )

    def process( self, is_only_filter: bool = False ) -> None:
        # https://docs.python.org/3/library/os.html#os.walk
        # https://stackoverflow.com/questions/11968976/list-files-only-in-the-current-directory
        # root, dirs, files
        for s, d, F in os.walk( self.da ):
            # print( s )
            # print( d )
            # print( F )
            for f in F:
                fp: str = os.path.join( s, f )

                if is_only_filter:
                    self.pkt_processor.process( fp )
                    continue

                self.tree.process(
                    self.sketch_processor.process(
                        self.pkt_processor.process( fp ),
                        fp
                    ),
                    fp
                )

    # TODO: csvparaser.TIMESTAMP_STR could vary.
    def __get_original_relative_time( self, da: str, h: str ):
        rt: float = sys.maxsize
        for s, d, F in os.walk( da ):
            for f in F:
                n: List = pandas.read_csv( h ).columns.values.tolist() if h is not None else None
                df: DataFrame = mapper.Mapper.mapping( pandas.read_csv( os.path.join( s, f ), names = n ) )
                for ( i, _ ) in df.iterrows():
                    rt = min( rt, df.loc[ i, csvparaser.TIMESTAMP_STR ] )

        self.l.debug( "rt: " + str( rt ) )
        return rt

    # DataProcessor( "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/data", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/NUSW-NB15_features_name.csv", None, 30 ).process( True )
    # DataProcessor( "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/data", None, None, 30 ).process( True )
