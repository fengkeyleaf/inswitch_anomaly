from typing import Dict

import imports.csvparaser as csvparaser
import imports.topo as topo

if __name__ == '__main__':
    cf:str = "./test/test_csv1_small.csv"
    # cf = "./test/test_csv1.csv"
    # cf = "../test/test_csv1_small_one_side_sending.csv"
    P:Dict = csvparaser.parse( cf )
    topo.CSVParaser().get_topo_json( P, "./pod-topo/topology.json" )