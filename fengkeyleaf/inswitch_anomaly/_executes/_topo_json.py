# -*- coding: utf-8 -*-

import os
import sys

# Directly called from the working directory.
"""
file:
description: File to process pkt input file to produce network topology.
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
from fengkeyleaf import topo

__version__ = "1.0"

if __name__ == '__main__':
    # _Tester().test1()
    # _Tester().test2()

    # # Initial Test
    # cf: str = "./test/test_csv1_small.csv"
    # cf: str = "../test/test_csv1_small_one_side_sending.csv"
    # cf: str = "./test/test_csv1.csv"
    # cf: str = "./test/result.csv"

    # Real-world data Test
    # cf: str = "/home/p4/tutorials/data/Bot-loT/dataSet/UNSW_2018_IoT_Botnet_Dataset_1_reformatted.csv"
    # cf = "/home/p4/tutorials/data/TON_loT/dataSet/Network_dataset_4_reformatted.csv"
    # cf = "/home/p4/tutorials/data/UNSW-NB15/dataSet/UNSW-NB15_3_reformatted.csv"

    cf = "/home/p4/BoT-loT/re-formatted/UNSW_2018_IoT_Botnet_Dataset_1_reformatted.csv"
    cf = "/home/p4/data/UNSW_2018_IoT_Botnet_Dataset_1_reformatted.csv"
    cf = "/home/p4/data/re-formatted/UNSW_2018_IoT_Botnet_Dataset_1_reformatted.csv"
    cf = "/home/p4/data/balanced_reformatted/UNSW_2018_IoT_Botnet_Dataset_1_balanced_reformatted.csv"

    # Basic forwarding test
    # cf = "/home/p4/tutorials/data/swtich_test/Bot-loT_1.csv"

    of: str = "./pod-topo/hosts/"
    topo.Builder.get_host_jsons(
        of,
        topo.Builder().get_topo_json(
            topo.Parser().parse( cf, "./pod-topo/pkts.json" ),
            "./pod-topo/topology.json"
        )
    )
