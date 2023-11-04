# -*- coding: utf-8 -*-

from typing import List

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.io import my_writer

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

# Process configs
IS_FROM_PRE_PROCESS_STR: str = "is_pre"
IS_FROM_SKETCH_STR: str = "is_sketch"
IS_FROM_TREE_STR: str = "is_tree"


# I/O
def get_output_file_path( f: str, fdn: str, sig: str ) -> str:
    """

    @param f: File path where the original data file is located.
    @param fdn: Folder name.
    @param sig: File signature name.
    @return:
    """
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
    # print( len( df ) )
    d: str = my_writer.get_dir( f ) + fdn
    # https://blog.finxter.com/how-to-save-a-text-file-to-another-folder-in-python/
    my_writer.make_dir( d )
    fn: str = my_writer.get_filename( f )
    fp: str = d + fn + sig

    return fp
