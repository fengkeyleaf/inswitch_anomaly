# -*- coding: utf-8 -*-

from typing import (
    Dict, List
)
from pandas import DataFrame

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

import fengkeyleaf.inswitch_anomaly as fkl_inswitch


class Mapper:
    """
    Class to get rid of unwanted features and mapping wanted ones to our favorite names.
    """
    # Pkt features mapping
    # https://www.geeksforgeeks.org/g-fact-34-class-or-static-variables-in-python/
    ID_M: Dict[ str, str ] = {
        "pkSeqID": fkl_inswitch.ID_STR, # UNSW_2018_IoT
        "No.": fkl_inswitch.ID_STR # csv by wireshark
    }
    SRC_IP_M: Dict[ str, str ] = {
        "saddr": fkl_inswitch.SRC_ADDR_STR, # UNSW_2018_IoT
        "src_ip": fkl_inswitch.SRC_ADDR_STR, # TON_IoT\Processed_Network_dataset
        "srcip": fkl_inswitch.SRC_ADDR_STR, # UNSW-NB15-CSV
        "Source": fkl_inswitch.SRC_ADDR_STR # csv by wireshark
    }
    SRC_MAC_M: Dict[ str, str ] = {
        "smac": fkl_inswitch.SRC_MAC_STR # UNSW_2018_IoT
    }
    DST_IP_M: Dict[ str, str ] = {
        "daddr": fkl_inswitch.DST_ADDR_STR, # UNSW_2018_IoT
        "dst_ip": fkl_inswitch.DST_ADDR_STR, # TON_IoT\Processed_Network_dataset
        "dstip": fkl_inswitch.DST_ADDR_STR, # UNSW-NB15-CSV
        "Destination": fkl_inswitch.DST_ADDR_STR # csv by wireshark
    }
    DST_MAC_M: Dict[ str, str ] = {
        "dmac": fkl_inswitch.DST_MAC_STR # UNSW_2018_IoT
    }
    LABEL_M: Dict[ str, str ] = {
        "attack": fkl_inswitch.LABEL_STR, # UNSW_2018_IoT
        "label": fkl_inswitch.LABEL_STR, # TON_IoT\Processed_Network_dataset
        "Label": fkl_inswitch.LABEL_STR # UNSW-NB15-CSV
    }
    TIME_M: Dict[ str, str ] = {
        "stime": fkl_inswitch.TIMESTAMP_STR, # UNSW_2018_IoT
        "Stime": fkl_inswitch.TIMESTAMP_STR, # UNSW-NB15-CSV
        "ts": fkl_inswitch.TIMESTAMP_STR, # TON_IoT\Processed_Network_dataset
        "Time": fkl_inswitch.TIMESTAMP_STR # csv by wireshark
    }
    SRC_PKTS_M: Dict[ str, str ] = {
        "spkts": fkl_inswitch.SRC_PKTS_STR, # BoT-IoT
        "src_pkts": fkl_inswitch.SRC_PKTS_STR, # TON_IoT
        "Spkts": fkl_inswitch.SRC_PKTS_STR # UNSW-NB15
    }
    DST_PKTS_M: Dict[ str, str ] = {
        "dpkts": fkl_inswitch.DST_PKTS_STR, # BoT-IoT
        "dst_pkts": fkl_inswitch.DST_PKTS_STR, # TON_IoT
        "Dpkts": fkl_inswitch.DST_PKTS_STR # UNSW-NB15
    }
    SRC_BYTES_M: Dict[ str, str ] = {
        "sbytes": fkl_inswitch.SRC_BYTES_STR, # BoT-IoT, UNSW-NB15
        "src_bytes": fkl_inswitch.SRC_BYTES_STR # TON_IoT
    }
    DST_BYTES_M: Dict[ str, str ] = {
        "dbytes": fkl_inswitch.DST_BYTES_STR, # BoT-IoT, UNSW-NB15
        "dst_bytes": fkl_inswitch.DST_BYTES_STR # TON_IoT
    }
    # Computed features mapping
    SRC_COUNT_M: Dict[ str, str ] = {
        fkl_inswitch.SRC_COUNT_STR: fkl_inswitch.SRC_COUNT_STR
    }
    SRC_TLS_M: Dict[ str, str ] = {
        fkl_inswitch.SRC_TLS_STR: fkl_inswitch.SRC_TLS_STR
    }
    DST_COUNT_M: Dict[ str, str ] = {
        fkl_inswitch.DST_COUNT_STR: fkl_inswitch.DST_COUNT_STR
    }
    DST_TLS_M: Dict[ str, str ] = {
        fkl_inswitch.DST_TLS_STR: fkl_inswitch.DST_TLS_STR
    }
    D: List[ Dict ] = [
        # Pkt features mapping
        ID_M, SRC_IP_M, SRC_MAC_M,
        DST_IP_M, DST_MAC_M, LABEL_M, TIME_M,
        SRC_PKTS_M, DST_PKTS_M, SRC_BYTES_M, DST_BYTES_M,
        # Computed features mapping
        SRC_COUNT_M, SRC_TLS_M, DST_COUNT_M, DST_TLS_M
    ]

    @staticmethod
    def mapping( df: DataFrame ) -> DataFrame:
        """
        Mapping feature names.
        @param df:
        @return:
        """
        dl: List[ str ] = []
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.keys.html#pandas.DataFrame.keys
        # todo: be careful with d.keys(), and we change d in the loop, this is not good, but not bad effect.
        for k in df.keys():
            h = Mapper._look_for_targeted_header( k )
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
    def _look_for_targeted_header( k: str ) -> str | None:
        for d in Mapper.D:
            if d.get( k ) is not None:
                return d.get( k )

        return None
