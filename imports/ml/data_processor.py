# -*- coding: utf-8 -*-

import argparse
import sys

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

import pkt_processor
import sketch_write
import tree
sys.path.append( "../com/fengkeyleaf/logging/" )
import my_logging

# parent-directory..
#     | --> original_data..
#     | --> mixed_data..
#     | --> preprocessed_data..
#     | --> sketches..
#     | --> trees..
#     | --> header ( optional )


# python .\data_processor.py -da "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\data" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv" -dm "D:\data"
# python .\data_processor.py -da "D:\data1\orignal" -he "C:\Users\fengk\OneDrive\documents\computerScience\RIT\2023 spring\NetworkingResearch\data\BoT-IoT\UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv" -dm "D:\data1\madeup" -ll 10
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
    ll: int = my_logging.get_level_name( args.logging_level )
    # pre-processing
    pkt_processor.PktProcessor( args.dir_data, args.header, args.dir_madeup, ll )
    # sketch
    sketch_write.SketchWriter( args.dir_data + pkt_processor.PktProcessor.FOLDER_NAME, args.dir_data, ll )
    # decision tree training.
    tree.Tree( args.dir_data + sketch_write.SketchWriter.FOLDER_NAME, args.dir_data, ll )