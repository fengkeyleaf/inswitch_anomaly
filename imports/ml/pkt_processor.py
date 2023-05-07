# -*- coding: utf-8 -*-

import math
import os
import re
from argparse import (
    ArgumentParser
)
from typing import (
    Dict, List, Tuple, Set
)
import sys

import pandas
from pandas import (
    DataFrame
)

import logging

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
        @Riley McGinn
"""

import sketch_write
import tree
import mix_make_ups
import mapper
# https://www.geeksforgeeks.org/python-import-module-from-different-directory/
# https://www.w3docs.com/snippets/python/importing-files-from-different-folder.html
sys.path.append( "../" )
import csvparaser
sys.path.append( "../com/fengkeyleaf/io/" )
import my_writer
sys.path.append( "../com/fengkeyleaf/logging/" )
import my_logging

IP_REG = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"  # raw string


# TODO: too many for s, d, F in os.walk( da ):
# TODO: Parallel computing.
# TODO: Verify pk ids.
class PktProcessor:
    FOLDER_NAME = "/re-formatted/"
    SIGNATURE = "_reformatted.csv"

    def __init__( self, da: str, h: str, dm: str, ll: int = logging.INFO ) -> None:
        """

        @param d: Directory to data set
        @param h: Path to features(headers)
        @param ll: logging level
        """
        # Logging setting
        # https://docs.python.org/3/library/logging.html#logging-levels
        self.l: logging.Logger = my_logging.get_logger( ll )
        self.l.debug( "da: " + da )
        self.l.debug( "h: " + h )
        self.l.debug( "dm: " + dm )

        assert da is not None
        self.h: str = h # header file path
        self.m: mix_make_ups.Mixer = mix_make_ups.Mixer( dm, self.get_original_relative_time( da ), ll )
        self.pre_process( da )

    def pre_process( self, dir: str ) -> None:
        # https://docs.python.org/3/library/os.html#os.walk
        # https://stackoverflow.com/questions/11968976/list-files-only-in-the-current-directory
        # root, dirs, files
        for s, d, F in os.walk( dir ):
            # print( s )
            # print( d )
            # print( F )
            for f in F:
                self.on_process( os.path.join( s, f ) )

    def on_process( self, f: str ) -> None:
        df: DataFrame = self.add_header( f )
        df = mapper.Mapper.mapping( df )
        df = self.m.mix( df )
        PktProcessor.spoof_macs( df )
        PktProcessor.renumber( df )
        assert PktProcessor.verify( df, f )

        # Write to file
        self.write( df, f )

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

    # TODO: Simplify
    def get_original_relative_time( self, da: str ):
        rt: float = sys.maxsize
        for s, d, F in os.walk( da ):
            for f in F:
                df: DataFrame = mapper.Mapper.mapping( pandas.read_csv( os.path.join( s, f ), names = pandas.read_csv( self.h ).columns.values.tolist() ) )
                for ( i, s ) in df.iterrows():
                    rt = min( rt, df.loc[ i, csvparaser.TIMESTAMP_STR ] )

        self.l.debug( "rt: " + str( rt ) )
        return rt


# python .\pkt_processor.py -d "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\data" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
#  python .\pkt_processor.py -d "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\TON_IoT\Processed_Network_dataset"
# python .\sketch_write.py "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\New folder\re-formatted\UNSW_2018_IoT_Botnet_Dataset_1_reformatted.csv" "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\New folder\re-formatted\UNSW_2018_IoT_Botnet_Dataset_1_sketch.csv"
# python .\tree.py -s "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\New folder\re-formatted\UNSW_2018_IoT_Botnet_Dataset_1_sketch.csv" -dt "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\New folder\re-formatted\UNSW_2018_IoT_Botnet_Dataset_1_tree.txt"
if __name__ == '__main__':
    parser: ArgumentParser = ArgumentParser()
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    # TODO: dir has not sub-directory
    parser.add_argument(
        "-d", "--dir",
        type = str, help = "Directory to data set", required = True
    )
    parser.add_argument(
        "-he", "--header",
        type = str, help = "Path to features(headers)", required = False, default = None
    )
    parser.add_argument(
        "-ll", "--logging-level",
        type = str, help = "Logging Level", required = False, default = logging.INFO
    )


    args = parser.parse_args()
    # https://www.programiz.com/python-programming/methods/string/endswith
    assert not args.dir.endswith( "/" ) or not args.dir.endswith( "\\" )
    # pre-processing
    PktProcessor( args.dir, args.header, args.logging_level )
    # sketch
    sketch_write.SketchWriter( args.dir + PktProcessor.FOLDER_NAME, args.dir, args.logging_level )
    # decision tree training.
    tree.Tree( args.dir + sketch_write.SketchWriter.FOLDER_NAME, args.dir, args.logging_level )


