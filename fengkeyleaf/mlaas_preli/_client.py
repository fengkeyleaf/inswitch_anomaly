# -*- coding: utf-8 -*-

import logging
from time import sleep
import os
import sys

"""
file:
description: Start a worker from an outside directory to use the package spacename, fengkeyleaf.
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
        '../../'
    )
)
from fengkeyleaf import worker

__version__ = "1.0"


if __name__ == '__main__':
    lr: float = 0.001
    w: worker.Worker = worker.Worker( lr, logging.INFO )
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
    f1: str = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/pima-indians-diabetes.data_part1.csv"
    f2: str = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/pima-indians-diabetes.data_part2.csv"
    # Inequal size
    # f = "fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_part1.csv"
#     f = "fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_part2.csv"
    w.load_data( f1, f )

    sleep( 2 ) # Wait for the receiver to initialize.
    w.training( 0 )
    w.evaluate()
