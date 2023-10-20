# -*- coding: utf-8 -*-

from typing import Dict
import json

"""
file: Generate network topology json file for p4 program to build the network.
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf import (
    csvparaser,
    topo,
    my_writer
)


def __get_host_json( d: Dict ) -> None:
    d: Dict = d[ topo.HOST_STR ]
    for k in d:
        assert d.get( k ) is not None
        my_writer.write_to_file(
             "./pod-topo/hosts/" + k + ".json",
             json.dumps( d[ k ], indent = 4 )
        )


if __name__ == '__main__':
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

    # Basic forwarding test
    # cf = "/home/p4/tutorials/data/swtich_test/Bot-loT_1.csv"

    P: Dict[ float, Dict ] = csvparaser.Parser().parse( cf )
    __get_host_json( topo.CSVParaser().get_topo_json( P, "pod-topo/topology.json" ) )
