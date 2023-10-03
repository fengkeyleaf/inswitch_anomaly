# -*- coding: utf-8 -*-

import logging

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
    w: Worker = Worker( lr, logging.DEBUG )
    w.build_model()
    w.load_data( "./fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data.csv" )
    w.training()
    w.evaluate()
