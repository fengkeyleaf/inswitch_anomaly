# -*- coding: utf-8 -*-

import argparse
import sys
import os

# Directly called from the working directory.
"""
file: Coordinator program to do the pkt data pre-processing and ML training,
      including re-formatting, data sampling/balancing, sketching, and training.
description:
nots: Directly called from the working directory.
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
import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf import my_logging, data_processor, filter as fkl_filter

__version__ = "1.0"

# BoT-IoT
# python .\fengkeyleaf\inswitch_anomaly\_executes\_data_pro.py -da "D:\networking\datasets\anomoaly_detection\BoT-loT" -he "D:\networking\datasets\anomoaly_detection\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv" -iwe True -lim 8 -inb True
# python .\fengkeyleaf\inswitch_anomaly\_executes\_data_pro.py -da "D:\data1\orignal" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv" -dm "D:\data1\madeup" -ll debug

# TON_IoT\Processed_Network_dataset
# python .\_data_pro.py -da "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\TON_IoT\Processed_Network_dataset\test" -dm "D:\data"

# UNSW-NB15
# python .\_data_pro.py -da "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\UNSW-NB15-CSV\data" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\UNSW-NB15-CSV\NUSW-NB15_features_name.csv" -dm "D:\data"

# Presentation, Milestone 2
# python .\_data_pro.py -da "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\thesis\presentation\sketching_csv_examples" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
if __name__ == '__main__':
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    # TODO: dir has not sub-directory
    parser.add_argument(
        "-da", "--dir-data",
        type = str, help = "Directory to data set", required = True
    )
    parser.add_argument(
        "-dm", "--dir-madeup",
        type = str, help = "Directory to made-up data set", required = False, default = None
    )
    parser.add_argument(
        "-he", "--header",
        type = str, help = "Path to features(headers)", required = False, default = None
    )
    parser.add_argument(
        "-iwe", "--is-writing_eval",
        type = str, help = "Is writing evaluating results", required = False, default = False
    )
    parser.add_argument(
        "-inb", "--is-not-balancing",
        type = str, help = "Is enabling data balancing", required = False, default = False
    )
    parser.add_argument(
        "-lim", "--sketch-lim",
        type = int, help = "Sketch limitation", required = False, default = -1
    )
    parser.add_argument(
        "-ll", "--logging-level",
        type = str, help = "Logging Level", required = False, default = "INFO"
    )

    args = parser.parse_args()
    # https://www.programiz.com/python-programming/methods/string/endswith
    assert not args.dir_data.endswith( "/" ) or not args.dir_data.endswith( "\\" )
    data_processor.DataProcessor(
        args.dir_data, args.header,
        args.dir_madeup, None,
        args.is_writing_eval,args.is_not_balancing, fkl_filter.ipv4_filter,
        my_logging.get_level_name( args.logging_level )
    ).process(
        {
          fkl_inswitch.IS_FROM_PRE_PROCESS_STR: True
        },
        {
            fkl_inswitch.IS_SKETCHING_STR: True,
            fkl_inswitch.IS_OPTIMIZING_STR: False,
            fkl_inswitch.LIMITATION_STR: args.sketch_lim,
            # Must be True since there is no balancing in the switch.
            # No meaning to enable it to evaluate trees.
            fkl_inswitch.IS_NOT_BALANCING_STR: True
        }
    )
