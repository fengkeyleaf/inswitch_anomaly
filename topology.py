from typing import Dict
import json

"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from imports.csvparaser import Parser
import imports.topo as topo
from imports.com.fengkeyleaf.io import my_writer as writer

def __get_host_json( d:Dict ) -> None:
    d:Dict = d[ topo.HOST_STR ]
    for k in d:
        assert d.get( k ) is not None
        writer.write_to_file(
             "./pod-topo/" + k + ".json",
             json.dumps( d[ k ], indent = 4 )
        )


if __name__ == '__main__':
    cf: str = "./test/test_csv1_small.csv"
    # cf: str = "../test/test_csv1_small_one_side_sending.csv"
    # cf: str = "./test/test_csv1.csv"
    cf: str = "./test/result.csv"
    
    P: Dict = Parser().parse( cf )
    __get_host_json( topo.CSVParaser().get_topo_json( P, "./pod-topo/topology.json" ) )