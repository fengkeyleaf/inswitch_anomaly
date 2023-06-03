# -*- coding: utf-8 -*-

from typing import List

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# Pkt features
ID_STR = "No."
TIMESTAMP_STR = "stime"
SRC_ADDR_STR = "Source"
SRC_MAC_STR = "srcMAC"
DST_ADDR_STR = "Destination"
DST_MAC_STR = "dstMAC"
LABEL_STR = "Label"
SRC_PKTS_STR = "spkts"
SRC_BYTES_STR = "sbytes"
DST_PKTS_STR = "dpkts"
DST_BYTES_STR = "dbytes"

# Computed features
SRC_COUNT_STR = "srcCount"
SRC_TLS_STR = "srcTLS"
DST_COUNT_STR = "dstCount"
DST_TLS_STR = "dstTLS"

# Label types
GOOD_LABEL_STR = "0"
BAD_LABEL_STR = "1" # attack pkt

# Sketch strings
RANGE_STR = "range"
GOOD_LABEL = 0
BAD_LABEL = 1 # attack pkt

# current wanted feature names
COLUMN_NAMES: List[ str ] = [
    SRC_COUNT_STR, SRC_TLS_STR,
    DST_COUNT_STR, DST_TLS_STR,
    LABEL_STR
]

# Wanted feature names
FEATURE_NAMES: List[ str ] = [ SRC_COUNT_STR, SRC_TLS_STR, DST_COUNT_STR, DST_TLS_STR ]