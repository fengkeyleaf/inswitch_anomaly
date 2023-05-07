# -*- coding: utf-8 -*-

import sys
from typing import (
    Dict, List, Tuple, Set
)
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

sys.path.append( "../" )
import csvparaser


class Mapper:
    # https://www.geeksforgeeks.org/g-fact-34-class-or-static-variables-in-python/
    id_M: Dict[ str, str ] = {
        "pkSeqID": csvparaser.ID_STR, # UNSW_2018_IoT
        "No.": csvparaser.ID_STR # csv by wireshark
    }
    src_ip_M: Dict[ str, str ] = {
        "saddr": csvparaser.SRC_ADDR_STR, # UNSW_2018_IoT
        "src_ip": csvparaser.SRC_ADDR_STR, # TON_IoT\Processed_Network_dataset
        "Source": csvparaser.SRC_ADDR_STR # csv by wireshark
    }
    src_mac_M: Dict[ str, str ] = {
        "smac": csvparaser.SRC_MAC_STR # UNSW_2018_IoT
    }
    dst_ip_M: Dict[ str, str ] = {
        "daddr": csvparaser.DST_ADDR_STR, # UNSW_2018_IoT
        "dst_ip": csvparaser.DST_ADDR_STR, # TON_IoT\Processed_Network_dataset
        "Destination": csvparaser.DST_ADDR_STR # csv by wireshark
    }
    dst_mac_M: Dict[ str, str ] = {
        "dmac": csvparaser.DST_MAC_STR # UNSW_2018_IoT
    }
    label_M: Dict[ str, str ] = {
        "attack": csvparaser.LABEL_STR, # UNSW_2018_IoT
        "label": csvparaser.LABEL_STR # TON_IoT\Processed_Network_dataset
    }
    time_M: Dict[ str, str ] = {
        "stime": csvparaser.TIMESTAMP_STR, # UNSW_2018_IoT
        "Time": csvparaser.TIMESTAMP_STR # csv by wireshark
    }

    @staticmethod
    def mapping( df: DataFrame ) -> DataFrame:
        dl: List[ str ] = [ ]
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.keys.html#pandas.DataFrame.keys
        # todo: be careful with d.keys(), and we change d in the loop, this is not good, but not bad effect.
        for k in df.keys():
            h = Mapper.look_for_targeted_header( k )
            # Skip the feature with the same name.
            if h == k: continue;

            # Replace feature name.
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
            Mapper.id_M, Mapper.src_ip_M, Mapper.src_mac_M,
            Mapper.dst_ip_M, Mapper.dst_mac_M, Mapper.label_M, Mapper.time_M
        ]

        for d in D:
            if d.get( k ) is not None:
                return d.get( k )

        return None