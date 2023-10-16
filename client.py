# -*- coding: utf-8 -*-

import logging
from time import sleep

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com

"""

from fengkeyleaf.mlaas_preli.worker import Worker

__version__ = "1.0"


if __name__ == '__main__':
    lr: float = 0.001
    w: Worker = Worker( lr, logging.INFO )
    w.build_model()
    # Full dataset
    f: str = "./fengkeyleaf/other/neural_network/pima-indians-diabetes.data.csv"
    # Partial dataset
    # One client
#     f = "./fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_small.csv"
    # Two clients
    # Both have partial data sets.
    # Equal size, small
    # f = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/small/pima-indians-diabetes.data_part1.csv"
    # f = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/small/pima-indians-diabetes.data_part2.csv"
    # Normal
    # f = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/pima-indians-diabetes.data_part1.csv"
    f = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/pima-indians-diabetes.data_part2.csv"
    # Inequal size
    # f = "fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_part1.csv"
#     f = "fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_part2.csv"
    w.load_data( f )

    sleep( 2 ) # Wait for the receiver to initialize.
    w.training()
    w.evaluate()
