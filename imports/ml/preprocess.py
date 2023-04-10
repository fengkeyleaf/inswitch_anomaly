import os
from argparse import (
    ArgumentParser
)
from typing import (
    Dict, List, Tuple
)
import sys

import pandas
from pandas import (
    DataFrame
)

"""
file:
description:
language: python3 3.11.3
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# https://www.geeksforgeeks.org/python-import-module-from-different-directory/
# https://www.w3docs.com/snippets/python/importing-files-from-different-folder.html
sys.path.append( "../" )
import csvparaser

class Proprocessor:
    # https://www.geeksforgeeks.org/g-fact-34-class-or-static-variables-in-python/
    id_M: Dict[ str, str ] = {
        "pkSeqID": csvparaser.ID_STR # UNSW_2018_IoT
    }
    src_ip_M: Dict[ str, str ] = {
        "saddr": csvparaser.SRC_ADDR_STR # UNSW_2018_IoT
    }
    src_mac_M: Dict[ str, str ] = {
        "smac": csvparaser.SRC_MAC_STR # UNSW_2018_IoT
    }
    dst_ip_M: Dict[ str, str ] = {
        "daddr": csvparaser.DST_ADDR_STR # UNSW_2018_IoT
    }
    dst_mac_M: Dict[ str, str ] = {
        "dmac": csvparaser.DST_MAC_STR # UNSW_2018_IoT
    }
    label_M: Dict[ str, str ] = {
        "attack": csvparaser.LABEL_STR # UNSW_2018_IoT
    }

    FOLDER_NAME = "/re-formatted/"
    SIGNATURE = "_reformatted.csv"

    def __init__( self, d: str, h: str ) -> None:
        assert d is not None
        self.F: List[ str ] = None
        self.h: str = None
        self.F, self.h = Proprocessor.get_files( d, h )
        self.pro_process()

    @staticmethod
    def get_files( d: str, h: str ) -> Tuple[ List[ str ], str ]:
        P: List[ str ] = []
        # https://docs.python.org/3/library/os.html#os.walk
        # https://stackoverflow.com/questions/11968976/list-files-only-in-the-current-directory
        for s, d, F in os.walk( d ):
            # print( s )
            # print( d )
            # print( F )
            for f in F:
                P.append( os.path.join( s, f ) )

        return ( P, h )

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

    def pro_process( self ) -> None:
        D: List[ DataFrame ] = self.add_header()
        self.mapping( D )
        # write to file.
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
        # print( len( D ) )
        assert len( self.F ) == len( D )
        for i in range( len( D ) ):
            # https://www.geeksforgeeks.org/python-program-to-get-the-file-name-from-the-file-path/
            # https://note.nkmk.me/en/python-os-basename-dirname-split-splitext/
            fp: str = os.path.dirname( self.F[ i ] )
            fn: str = os.path.splitext( os.path.basename( self.F[ i ] ) )[ 0 ]
            print( fp + "/" + fn + Proprocessor.SIGNATURE )
            d: str = fp + Proprocessor.FOLDER_NAME
            # https://blog.finxter.com/how-to-save-a-text-file-to-another-folder-in-python/
            if not os.path.isdir( d ):
                os.mkdir( d )

            D[ i ].to_csv( d + fn + Proprocessor.SIGNATURE, index = False )

    def add_header( self ) -> List[ DataFrame ]:
        # https://www.geeksforgeeks.org/how-to-append-a-new-row-to-an-existing-csv-file/
        # https://www.usepandas.com/csv/append-csv-files
        D: List[ DataFrame ] = []
        # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
        for f in self.F:
            hf = pandas.read_csv( self.h )
            # print( type( hf.columns.values.tolist() ))
            # https://datascienceparichay.com/article/get-column-names-as-list-in-pandas-dataframe/
            cf = pandas.read_csv( f, names = hf.columns.values.tolist() )
            # https://pandas.pydata.org/docs/reference/api/pandas.concat.html
            D.append( pandas.concat( [ hf, cf ] ) )

        return D

    def mapping( self, D: List[ DataFrame ] ) -> None:
        for i in range( len( D ) ):
            d: DataFrame = D[ i ]
            dl: List[ str ] = []
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.keys.html#pandas.DataFrame.keys
            # todo: be careful with d.keys(), and we change d in the loop, this is not good, but not bad effect.
            for k in d.keys():
                h = Proprocessor.look_for_targeted_header( k )
                if h is not None:
                    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html
                    d = d.rename( columns = { k: h } )
                else:
                    dl.append( k )

            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html
            # print( dl )
            # d.drop( dl, axis = 1 )
            D[ i ] = d.drop( columns = dl )



# python .\preprocess.py -d "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\data" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
# python .\sketch_write.py "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\New folder\re-formatted\UNSW_2018_IoT_Botnet_Dataset_1_reformatted.csv" "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\New folder\re-formatted\UNSW_2018_IoT_Botnet_Dataset_1_sketch.csv"
if __name__ == '__main__':
    parser:ArgumentParser = ArgumentParser()
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    parser.add_argument( "-d", "--dir", type = str, help="directory to data set", required = True )
    parser.add_argument( "-he", "--header", type = str, help="Path to features(headers)", required = False, default = None )

    args = parser.parse_args()
    Proprocessor( args.dir, args.header )

