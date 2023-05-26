# -*- coding: utf-8 -*-

from typing import (
    Dict, List
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

from fengkeyleaf.inswtich_anomaly import (
    csvparaser
)


class Mapper:
    """
    Class to get rid of unwanted features and mapping wanted ones to our favorite names.
    """
    # https://www.geeksforgeeks.org/g-fact-34-class-or-static-variables-in-python/
    ID_M: Dict[ str, str ] = {
        "pkSeqID": csvparaser.ID_STR, # UNSW_2018_IoT
        "No.": csvparaser.ID_STR # csv by wireshark
    }
    SRC_IP_M: Dict[ str, str ] = {
        "saddr": csvparaser.SRC_ADDR_STR, # UNSW_2018_IoT
        "src_ip": csvparaser.SRC_ADDR_STR, # TON_IoT\Processed_Network_dataset
        "srcip": csvparaser.SRC_ADDR_STR, # UNSW-NB15-CSV
        "Source": csvparaser.SRC_ADDR_STR # csv by wireshark
    }
    SRC_MAC_M: Dict[ str, str ] = {
        "smac": csvparaser.SRC_MAC_STR # UNSW_2018_IoT
    }
    DST_IP_M: Dict[ str, str ] = {
        "daddr": csvparaser.DST_ADDR_STR, # UNSW_2018_IoT
        "dst_ip": csvparaser.DST_ADDR_STR, # TON_IoT\Processed_Network_dataset
        "dstip": csvparaser.DST_ADDR_STR, # UNSW-NB15-CSV
        "Destination": csvparaser.DST_ADDR_STR # csv by wireshark
    }
    DST_MAC_M: Dict[ str, str ] = {
        "dmac": csvparaser.DST_MAC_STR # UNSW_2018_IoT
    }
    LABEL_M: Dict[ str, str ] = {
        "attack": csvparaser.LABEL_STR, # UNSW_2018_IoT
        "label": csvparaser.LABEL_STR, # TON_IoT\Processed_Network_dataset
        "Label": csvparaser.LABEL_STR # UNSW-NB15-CSV
    }
    TIME_M: Dict[ str, str ] = {
        "stime": csvparaser.TIMESTAMP_STR, # UNSW_2018_IoT
        "Stime": csvparaser.TIMESTAMP_STR, # UNSW-NB15-CSV
        "ts": csvparaser.TIMESTAMP_STR, # TON_IoT\Processed_Network_dataset
        "Time": csvparaser.TIMESTAMP_STR # csv by wireshark
    }
    SRC_PKTS_M: Dict[ str, str ] = {
        "spkts": csvparaser.SRC_PKTS_STR, # BoT-IoT
        "src_pkts": csvparaser.SRC_PKTS_STR, # TON_IoT
        "Spkts": csvparaser.SRC_PKTS_STR # UNSW-NB15
    }
    DST_PKTS_M: Dict[ str, str ] = {
        "dpkts": csvparaser.DST_PKTS_STR, # BoT-IoT
        "dst_pkts": csvparaser.DST_PKTS_STR, # TON_IoT
        "Dpkts": csvparaser.DST_PKTS_STR # UNSW-NB15
    }
    SRC_BYTES_M: Dict[ str, str ] = {
        "sbytes": csvparaser.SRC_BYTES_STR, # BoT-IoT, UNSW-NB15
        "src_bytes": csvparaser.SRC_BYTES_STR # TON_IoT
    }
    DST_BYTES_M: Dict[ str, str ] = {
        "dbytes": csvparaser.DST_BYTES_STR, # BoT-IoT, UNSW-NB15
        "dst_bytes": csvparaser.DST_BYTES_STR # TON_IoT
    }


    @staticmethod
    def mapping( df: DataFrame ) -> DataFrame:
        dl: List[ str ] = []
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
            Mapper.ID_M, Mapper.SRC_IP_M, Mapper.SRC_MAC_M,
            Mapper.DST_IP_M, Mapper.DST_MAC_M, Mapper.LABEL_M, Mapper.TIME_M,
            Mapper.SRC_PKTS_M, Mapper.DST_PKTS_M, Mapper.SRC_BYTES_M, Mapper.DST_BYTES_M
        ]

        for d in D:
            if d.get( k ) is not None:
                return d.get( k )

        return None