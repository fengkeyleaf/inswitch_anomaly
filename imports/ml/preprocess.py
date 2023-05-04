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
# https://www.geeksforgeeks.org/python-import-module-from-different-directory/
# https://www.w3docs.com/snippets/python/importing-files-from-different-folder.html
sys.path.append( "../" )
import csvparaser
sys.path.append( "../com/fengkeyleaf/io/" )
import my_writer
sys.path.append( "../com/fengkeyleaf/utils/lang/" )
import my_math
sys.path.append( "../com/fengkeyleaf/logging/" )
import my_logging


# TODO: Parallel computing.
# TODO: Verify pk ids.
class Proprocessor:
    # https://www.geeksforgeeks.org/g-fact-34-class-or-static-variables-in-python/
    id_M: Dict[ str, str ] = {
        "pkSeqID": csvparaser.ID_STR # UNSW_2018_IoT
    }
    src_ip_M: Dict[ str, str ] = {
        "saddr": csvparaser.SRC_ADDR_STR, # UNSW_2018_IoT
        "src_ip": csvparaser.SRC_ADDR_STR # TON_IoT\Processed_Network_dataset
    }
    src_mac_M: Dict[ str, str ] = {
        "smac": csvparaser.SRC_MAC_STR # UNSW_2018_IoT
    }
    dst_ip_M: Dict[ str, str ] = {
        "daddr": csvparaser.DST_ADDR_STR, # UNSW_2018_IoT
        "dst_ip": csvparaser.DST_ADDR_STR # TON_IoT\Processed_Network_dataset
    }
    dst_mac_M: Dict[ str, str ] = {
        "dmac": csvparaser.DST_MAC_STR # UNSW_2018_IoT
    }
    label_M: Dict[ str, str ] = {
        "attack": csvparaser.LABEL_STR, # UNSW_2018_IoT
        "label": csvparaser.LABEL_STR # TON_IoT\Processed_Network_dataset
    }

    FOLDER_NAME = "/re-formatted/"
    SIGNATURE = "_reformatted.csv"

    def __init__( self, d: str, h: str, ll: int = logging.INFO ) -> None:
        """

        @param d: Directory to data set
        @param h: Path to features(headers)
        @param ll: logging level
        """
        # Logging setting
        # https://docs.python.org/3/library/logging.html#logging-levels
        self.l = my_logging.getLogger( ll )

        assert d is not None
        self.h: str = h # header file path
        self.pre_process( d )

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
        df = Proprocessor.mapping( df )
        Proprocessor.spoof_macs( df )
        Proprocessor.renumber( df )
        Proprocessor.verify( df, f )

        # write to file.
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
        # print( len( df ) )

        fp: str = my_writer.get_dir( f )
        fn: str = my_writer.get_filename( f )
        d: str = fp + Proprocessor.FOLDER_NAME
        # https://blog.finxter.com/how-to-save-a-text-file-to-another-folder-in-python/
        my_writer.make_dir( d )

        self.l.info( "pro-process: " + d + fn + Proprocessor.SIGNATURE )
        df.to_csv( d + fn + Proprocessor.SIGNATURE, index = False )


    def add_header( self, f: str ) -> DataFrame:
        # https://www.geeksforgeeks.org/how-to-append-a-new-row-to-an-existing-csv-file/
        # https://www.usepandas.com/csv/append-csv-files

        # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
        # Header is provided.
        if self.h:
            hf = pandas.read_csv( self.h )
            # print( type( hf.columns.values.tolist() ))
            # https://datascienceparichay.com/article/get-column-names-as-list-in-pandas-dataframe/
            cf = pandas.read_csv( f, names = hf.columns.values.tolist() )
            # https://pandas.pydata.org/docs/reference/api/pandas.concat.html
            return pandas.concat( [ hf, cf ] )

        # Default header is provided.
        return pandas.read_csv( f )

    @staticmethod
    def mapping( df: DataFrame ) -> DataFrame:
        dl: List[ str ] = [ ]
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.keys.html#pandas.DataFrame.keys
        # todo: be careful with d.keys(), and we change d in the loop, this is not good, but not bad effect.
        for k in df.keys():
            h = Proprocessor.look_for_targeted_header( k )
            if h is not None:
                # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html
                df = df.rename( columns = { k: h } )
            else:
                dl.append( k )

        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html
        # print( dl )
        # d.drop( dl, axis = 1 )
        return df.drop( columns = dl )


    @staticmethod
    def look_for_targeted_header( k: str ):
        D: List[ Dict ] = [
            Proprocessor.id_M, Proprocessor.src_ip_M, Proprocessor.src_mac_M,
            Proprocessor.dst_ip_M, Proprocessor.dst_mac_M, Proprocessor.label_M
        ]

        for d in D:
            if d.get( k ) is not None:
                return d.get( k )

        return None

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
            id = Proprocessor.create_mac( m, [ si, di ], id, S )

            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.loc.html
            assert m[ si ] is not None
            d.loc[ i, csvparaser.SRC_MAC_STR ] = m[ si ]
            assert m[ di ] is not None
            d.loc[ i, csvparaser.DST_MAC_STR ] = m[ di ]


    @staticmethod
    def create_mac( m: Dict[ str, str ], I: List[ str ], id: int, s: Set[ str ] ) -> int:
        for i in I:
            if m.get( i ) is None:
                m[ i ] = Proprocessor.create_MAC( id )
                assert m[ i ] not in s
                s.add( m[ i ] )

                id = my_math.add_one( id )
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
            id = my_math.add_one( id )

    IP_REG = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$" # raw string

    @staticmethod
    def verify( d: DataFrame, f: str ) -> None:
        # TODO: verify macs and ips
        for ( i, s ) in d.iterrows():
            assert re.search( Proprocessor.IP_REG, d.loc[ i , csvparaser.SRC_ADDR_STR ] )
            assert re.search( Proprocessor.IP_REG, d.loc[ i , csvparaser.DST_ADDR_STR ] )
            assert d.loc[ i, csvparaser.ID_STR ] != "" and d.loc[ i, csvparaser.ID_STR ] is not None
            assert d.loc[ i, csvparaser.LABEL_STR ] == 0 or d.loc[ i, csvparaser.LABEL_STR ] == 1, str( i ) + " | " + f


# python .\preprocess.py -d "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\data" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
#  python .\preprocess.py -d "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\TON_IoT\Processed_Network_dataset"
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
    Proprocessor( args.dir, args.header, args.logging_level )
    # sketch
    sketch_write.SketchWriter( args.dir + Proprocessor.FOLDER_NAME, args.dir, args.logging_level )
    # decision tree training.
    tree.Tree( args.dir + sketch_write.SketchWriter.FOLDER_NAME, args.dir, args.logging_level )


