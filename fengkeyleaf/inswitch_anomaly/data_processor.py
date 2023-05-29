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

from fengkeyleaf.io import (
    my_files,
    my_writer
)
from fengkeyleaf.logging import my_logging
from fengkeyleaf.inswitch_anomaly import (
    mapper,
    mix_make_ups,
    pkt_processor,
    sketch_write,
    tree
)
import fengkeyleaf.inswitch_anomaly as fkl_inswitch

# parent-directory..
#     | --> original_data..
#     | --> mixed_data..
#     | --> preprocessed_data..
#     | --> sketches..
#     | --> trees..
#     | --> header ( optional )


# fengkeyleaf.data_processor.DataProcessor( "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/data", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv", None, None, 20 ).process( True )
# fengkeyleaf.data_processor.DataProcessor( "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/data", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/NUSW-NB15_features_name.csv", None, None, 20 ).process( True )
# fengkeyleaf.data_processor.DataProcessor( "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/data", None, None, None, 20 ).process( True )
# TODO: Mix different group of data sets.
class DataProcessor:
    """
    Class to do the all tree processing steps:
    1) pkt processing;
    2) sketch processing;
    3) tree processing;
    """
    def __init__(
            self, da: str, h: str,
            dm: str = None, D: List[ str ] = None,
            ll: int = logging.INFO
    ) -> None:
        """

        @param da: Directory to the original data sets.
        @param h: Path to features(headers)
        @param dm: Directory to the synthesised data sets.
        @param D: List of directories to the processed data sets to test trees.
        @param ll: logging level
        """
        # Logging setting
        # https://docs.python.org/3/library/logging.html#logging-levels
        self.l: logging.Logger = my_logging.get_logger( ll )
        self.l.debug( "da: " + str( da ) )
        self.l.debug( "h: " + str( h ) )
        self.l.debug( "dm: " + str( dm ) )
        self.l.debug( "D: " + str( D ) )

        self.da: str = da
        assert da is not None
        # Initialize the three processors.
        self.pkt_processor: pkt_processor.PktProcessor = pkt_processor.PktProcessor(
            h,
            mix_make_ups.Mixer(
                dm,
                0 if dm is None or dm == "" else self.__get_original_relative_time( da, h ),
                ll
            ),
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
            D,
            False,
            ll
        )

    def process( self, is_only_filter: bool = False ) -> None:
        """
        Process data sets and train trees. Start from beginning.
        1) Re-format csv data sets.
        2) Generate sketch csv files.
        3) Train a tree with the sketch files.
        @param is_only_filter: True, only generate processed data sets.
        """
        self.l.info( "Start processing from the beginning." )

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
                    )[ 0 ],
                    fp
                )

    # TODO: csvparaser.TIMESTAMP_STR could vary.
    def __get_original_relative_time( self, da: str, h: str ) -> float:
        """
        Relative Time to align all pkts in the original data sets in timestamp order.
        @param da: Directory to the original data sets.
        @param h: Path to features(headers)
        @return:
        """
        rt: float = sys.maxsize
        for s, d, F in os.walk( da ):
            for f in F:
                n: List = pandas.read_csv( h ).columns.values.tolist() if h is not None else None
                df: DataFrame = mapper.Mapper.mapping( pandas.read_csv( os.path.join( s, f ), names = n ) )
                for ( i, _ ) in df.iterrows():
                    rt = min( rt, df.loc[ i, fkl_inswitch.TIMESTAMP_STR ] )

        self.l.debug( "rt: " + str( rt ) )
        return rt

    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/data"
    # h = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"

    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/data"

    # da = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/data"
    # h = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/NUSW-NB15_features_name.csv"

    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches" ]
    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/sketches", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/sketches" ]
    # D = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/processed/sketches", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/processed/sketches", "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/processed/sketches" ]

    # fengkeyleaf.data_processor.DataProcessor( da, h, None, D, 10 ).train_trees()
    # TODO: merge into process() in this class or train() in the Tree class.
    def train_trees( self ) -> None:
        """
        Train tree with given csv files.
        """
        self.l.info( "Start processing from generating trees." )

        for fp in my_files.get_files_in_dir( self.tree.d ):
            with open(
                    fp, encoding = my_files.UTF8,
                    errors = my_files.BACK_SLASH_REPLACE
            ) as f:
                assert my_writer.get_extension( fp ).lower() == my_files.CSV, fp
                self.tree.process(
                    pandas.read_csv( f ),
                    self.tree.pd + "/" + my_writer.get_filename( fp )
                )
