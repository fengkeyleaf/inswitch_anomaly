# -*- coding: utf-8 -*-

import sys
import os
from typing import Dict
import json

# Directly called from the working directory.
"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# fengkeyleaf imports
# Add path dependency, which is allowed to exclude this file from the working directory.
sys.path.append(
    os.path.join(
        os.path.dirname( os.path.abspath( __file__ ) ),
        '../../../'
    )
)
from fengkeyleaf import evaulator, my_writer

__version__ = "1.0"


if __name__ == '__main__':
    fp: str = "D:/networking/datasets/anomoaly_detection/New folder/re-formatted/UNSW_2018_IoT_Botnet_Dataset_2_reformatted.csv"
    with open( "./output_sample_2.json", "r" ) as f_json:
        D: Dict = json.load( f_json )
        evaulator.Evaluator().evaluate( fp, D )
        my_writer.write_to_file( evaulator.RESULT_FILE, json.dumps( D, indent = 4 ) )