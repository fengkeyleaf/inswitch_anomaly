# -*- coding: utf-8 -*-

from typing import Dict

import pandas as pd

"""
file: csvparaser.py
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

ID_STR = "No."
TIMESTAMP_STR = "stime"
SRC_ADDR_STR = "Source"
SRC_MAC_STR = "srcMAC"
DST_ADDR_STR = "Destination"
DST_MAC_STR = "dstMAC"
LABEL_STR = "Label"
GOOD_LABEL_STR = "0"
BAD_LABEL_STR = "1" # attack pkt


class Parser:
    def __init__( self ) -> None:
        pass

    @staticmethod
    def __assertion( a: str, m: str ) -> bool:
        D: Dict = {}
        if D.get( a ) is not None:
            assert D[ a ] == m
            return True

        D[ a ] = m
        return True

    # https://stackoverflow.com/questions/11706215/how-can-i-fix-the-git-error-object-file-is-empty/12371337#12371337
    def parse( self, f: str ) -> Dict[ float, Dict ]:
        """
        :param f: file path to the csv file.
        :return: { 
            pkt_id: {
                srcAddr: srcIP, dstAddr: dstIP,
                srcMAC: srcMac, dstMAC: dstMac,
                Label: Number( 0 or 1 )
            }
        }
        """
        dic: Dict[ float, Dict ] = {}
        id: int = 0
        # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
        # https://pandas.pydata.org/docs/reference/frame.html
        # https://www.geeksforgeeks.org/python-next-method/
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.html?highlight=series#pandas.Series
        for ( _, s ) in pd.read_csv( f ).iterrows():
            assert dic.get( s[ ID_STR ] ) is None, "Already seen this ID before."
            id = id + 1
            # if ( s[ ID_STR ] == 1 or s[ ID_STR ] == 2006 or s[ ID_STR ] == 2007 ):
            #     continue

            assert id <= int( s[ ID_STR ] ) # Consistent incremental id garaunteed
            assert s[ LABEL_STR ] == int( GOOD_LABEL_STR ) or s[ LABEL_STR ] == int( BAD_LABEL_STR ), type( s[ LABEL_STR ] )
            assert self.__assertion( s[ SRC_ADDR_STR ], s[ SRC_MAC_STR ] ) and self.__assertion( s[ DST_ADDR_STR ], s[ DST_MAC_STR ] )

            # print( "s=%s, d=%s" % ( s[ "Source" ], s[ "Destination" ] ) )
            dic[ s[ ID_STR ] ] = {
                SRC_ADDR_STR: s[ SRC_ADDR_STR ],
                DST_ADDR_STR: s[ DST_ADDR_STR ],
                SRC_MAC_STR: s[ SRC_MAC_STR ],
                DST_MAC_STR: s[ DST_MAC_STR ],
                LABEL_STR: s[ LABEL_STR ]
            }

        print( "csvparaser: %d pkts in this csv file" % ( id ) )
        return dic


if __name__ == '__main__':
    print( Parser().parse( "../test/test_csv1_small.csv" ) )