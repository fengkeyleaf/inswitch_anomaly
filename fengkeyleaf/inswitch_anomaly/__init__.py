# -*- coding: utf-8 -*-

from typing import List
from pandas import DataFrame

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

# Wanted sketch feature names
SKETCH_FEATURE_NAMES: List[ str ] = [ SRC_COUNT_STR, SRC_TLS_STR, DST_COUNT_STR, DST_TLS_STR ]
# Wanted pkt feature names
PKT_FEATURE_NAMES: List[ str ] = [ SRC_ADDR_STR, DST_ADDR_STR ]

# Tree Evaluation
LIMITATION_STR: str = "lims"
MEDIAN_ACCURACY_STR: str = "med_acc"

# Evaluation feature names
SKETCH_LIMITATION_OPTI_FEATURE_NAMES: List[ str ] = [ LIMITATION_STR, MEDIAN_ACCURACY_STR ]

# Sketch configs
# Parameters
IS_SKETCHING_STR: str = "is_sket"
IS_OPTIMIZING_STR: str = "is_opti"
IS_NOT_BALANCING_STR: str = "is_not_bal"
LIMITATION_STR: str = "lims"
OPTI_FUNCTION_CONFIG_STR: str = "op_f_config"

# Optimization function names
BINARY_OP: int = 0
LINEAR_OP: int = 1
