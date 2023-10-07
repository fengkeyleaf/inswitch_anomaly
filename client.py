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
    f: str = "./fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data.csv"
    f = "./fengkeyleaf/other/neural_network/pima-indians-diabetes.data.csv"
    w.load_data( f )

    sleep( 2 )
    w.training()
    w.evaluate()
