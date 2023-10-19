# -*- coding: utf-8 -*-

import argparse

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

from fengkeyleaf import data_processor, my_logging, filter

# BoT-IoT
# python .\data_pro.py -da "D:\networking\datasets\anomoaly_detection\BoT-loT" -he "D:\networking\datasets\anomoaly_detection\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
# python .\data_pro.py -da "D:\data1\orignal" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv" -dm "D:\data1\madeup" -ll debug

# TON_IoT\Processed_Network_dataset
# python .\data_pro.py -da "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\TON_IoT\Processed_Network_dataset\test" -dm "D:\data"

# UNSW-NB15
# python .\data_pro.py -da "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\UNSW-NB15-CSV\data" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\UNSW-NB15-CSV\NUSW-NB15_features_name.csv" -dm "D:\data"

# Presentation, Milestone 2
# python .\data_pro.py -da "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\thesis\presentation\sketching_csv_examples" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
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
        "-ll", "--logging-level",
        type = str, help = "Logging Level", required = False, default = "INFO"
    )

    args = parser.parse_args()
    # https://www.programiz.com/python-programming/methods/string/endswith
    assert not args.dir_data.endswith( "/" ) or not args.dir_data.endswith( "\\" )
    data_processor.DataProcessor(
        args.dir_data, args.header,
        args.dir_madeup, None,
        False,  filter.ipv4_filter,
        my_logging.get_level_name( args.logging_level )
    ).process()
