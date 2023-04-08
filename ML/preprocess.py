import os
from argparse import (
    ArgumentParser
)
from typing import (
    Dict, List, Tuple
)

import pandas
from pandas import ( DataFrame )

"""
file:
description:
language: python3 3.11.3
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""


class Proprocessor:
    # https://www.geeksforgeeks.org/g-fact-34-class-or-static-variables-in-python/
    id_M: Dict[ str, str ] = {

    }
    src_ip_M: Dict[ str, str ] = {

    }
    src_mac_M: Dict[ str, str ] = {

    }
    dst_ip_M: Dict[ str, str ] = {

    }
    dst_mac_M: Dict[ str, str ] = {

    }
    label_M: Dict[ str, str ] = {

    }

    signature = "_reformatted.csv"

    def __init__( self, d: str, h: str ) -> None:
        assert d is not None
        self.F: List[ str ] = None
        self.h: str = None
        self.F, self.h = Proprocessor.get_files( d, h )

    @staticmethod
    def get_files( d: str, h: str ) -> Tuple[ List[ str ], str ]:
        F: List[ str ] = []
        # https://docs.python.org/3/library/os.html#os.walk
        for s, d, fn in os.walk( d ):
            for f in fn:
                F.append( f )

        return ( F, h )

    @staticmethod
    def look_for_targeted_header( k: str ):
        D: List[ Dict ] = [
            Proprocessor.id_M, Proprocessor.src_ip_M, Proprocessor.src_mac_M,
            Proprocessor.dst_ip_M, Proprocessor.dst_mac_M, Proprocessor.label_M
        ]

        for d in D:
            if d.get( k ) is not None:
                d.get( k )

        return None

    def pro_process( self ) -> None:
        D: List[ DataFrame ] = self.add_header()
        self.mapping( D )
        # write to file.
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
        assert len( self.F ) == len( D )
        for i in range( len( D ) ):
            # https://www.geeksforgeeks.org/python-program-to-get-the-file-name-from-the-file-path/
            # https://note.nkmk.me/en/python-os-basename-dirname-split-splitext/
            fp = os.path.dirname( self.F[ i ] )
            fn = os.path.splitext( os.path.basename( self.F[ i ] ) )[ 0 ]
            D[ i ].to_csv( fp + fn + Proprocessor.signature )

    def add_header( self ) -> List[ DataFrame ]:
        # https://www.geeksforgeeks.org/how-to-append-a-new-row-to-an-existing-csv-file/
        # https://www.usepandas.com/csv/append-csv-files
        D: List[ DataFrame ] = []
        # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
        for f in self.F:
            hf = pandas.read_csv( self.h )
            cf = pandas.read_csv( f )
            # https://pandas.pydata.org/docs/reference/api/pandas.concat.html
            D.append( pandas.concat( [ hf, cf ] ) )

        return D

    def mapping( self, D: List[ DataFrame ] ) -> None:
        for d in D:
            dl: List[ str ] = []
            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.keys.html#pandas.DataFrame.keys
            for k in d.keys():
                h = Proprocessor.look_for_targeted_header( k )
                if h is not None:
                    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.rename.html
                    d.rename( columns = { k: h } )
                else:
                    dl.append( k )

            # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html
            d.drop( dl )



if __name__ == '__main__':
    parser:ArgumentParser = ArgumentParser()
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    parser.add_argument( "-d", "--dir", type = str, help="directory to data set", required = True )
    parser.add_argument( "-h", "--header", type = str, help="Path to features(headers)", required = False, default = None )

    args = parser.parse_args()
    Proprocessor( args.dir, args.header )

