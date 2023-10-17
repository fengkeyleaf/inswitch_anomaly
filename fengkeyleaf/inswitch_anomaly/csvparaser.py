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

import fengkeyleaf.inswitch_anomaly as fkl_inswitch


class Parser:
    """
    Parse processed pkt csv files into a dict.
    """
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
    @staticmethod
    def parse( f: str ) -> Dict[ float, Dict ]:
        """
        Class to parse processed pkt csv files into a dict.
        The file should be in the standard format, that is, all features are mapping to our own ones.
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
            assert dic.get( s[ fkl_inswitch.ID_STR ] ) is None, "Already seen this ID before."
            id = id + 1
            # if ( s[ ID_STR ] == 1 or s[ ID_STR ] == 2006 or s[ ID_STR ] == 2007 ):
            #     continue

            assert id <= int( s[ fkl_inswitch.ID_STR ] ) # Consistent incremental id garaunteed
            assert s[ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.GOOD_LABEL_STR ) or s[ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.BAD_LABEL_STR ), type( s[ fkl_inswitch.LABEL_STR ] )
            assert Parser.__assertion( s[ fkl_inswitch.SRC_ADDR_STR ], s[ fkl_inswitch.SRC_MAC_STR ] ) and Parser.__assertion( s[ fkl_inswitch.DST_ADDR_STR ], s[ fkl_inswitch.DST_MAC_STR ] )

            # print( "s=%s, d=%s" % ( s[ "Source" ], s[ "Destination" ] ) )
            dic[ s[ fkl_inswitch.ID_STR ] ] = {
                fkl_inswitch.SRC_ADDR_STR: s[ fkl_inswitch.SRC_ADDR_STR ],
                fkl_inswitch.DST_ADDR_STR: s[ fkl_inswitch.DST_ADDR_STR ],
                fkl_inswitch.SRC_MAC_STR: s[ fkl_inswitch.SRC_MAC_STR ],
                fkl_inswitch.DST_MAC_STR: s[ fkl_inswitch.DST_MAC_STR ],
                fkl_inswitch.LABEL_STR: s[ fkl_inswitch.LABEL_STR ]
            }

        print( "csvparaser: %d pkts in this csv file" % ( id ) )
        return dic


if __name__ == '__main__':
    print( Parser().parse( "../test/test_csv1_small.csv" ) )
