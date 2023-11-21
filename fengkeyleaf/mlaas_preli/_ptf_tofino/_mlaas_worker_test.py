# -*- coding: utf-8 -*-

################################################################################
# BAREFOOT NETWORKS CONFIDENTIAL & PROPRIETARY
#
# Copyright (c) 2018-2019 Barefoot Networks, Inc.

# All Rights Reserved.
#
# NOTICE: All information contained herein is, and remains the property of
# Barefoot Networks, Inc. and its suppliers, if any. The intellectual and
# technical concepts contained herein are proprietary to Barefoot Networks,
# Inc.
# and its suppliers and may be covered by U.S. and Foreign Patents, patents in
# process, and are protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material is
# strictly forbidden unless prior written permission is obtained from
# Barefoot Networks, Inc.
#
# No warranty, explicit or implicit is provided, unless granted under a
# written agreement with Barefoot Networks, Inc.
#
#
###############################################################################

import logging
from time import sleep

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# This import should go first
# because it will add a py path to the system to import the package, fengkeyleaf
import _mlaas_preli
# fengkeyleaf imports
from fengkeyleaf import woker_tofino

__version__ = "1.0"


class WorkerTestGroup( _mlaas_preli.MlaasBaseProgramTest ):
    # Full dataset
    FULL_DATASET: str = "./fengkeyleaf/other/neural_network/pima-indians-diabetes.data.csv"
    # Partial dataset
    # One client
    ONE_CLIENT_DATASET: str = "./fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_small.csv"
    # Two clients
    # Both have partial data sets.
    # Equal size, small
    # f = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/small/pima-indians-diabetes.data_part1.csv"
    # f = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/small/pima-indians-diabetes.data_part2.csv"
    # Normal
    # f1: str = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/pima-indians-diabetes.data_part1.csv"
    # f2: str = "./fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/pima-indians-diabetes.data_part2.csv"
    # Inequal size
    # f = "fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_part1.csv"
    # f = "fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_part2.csv"
    pass


# @tu.disabled
class OneClientTestCase1( WorkerTestGroup ):
    def runTest( self ) -> None:
        lr: float = 0.001

        w: woker_tofino.Worker = woker_tofino.Worker( lr, logging.INFO )
        w.config_receiver( self.ig_port )
        w.build_model()
        w.load_data( OneClientTestCase1.ONE_CLIENT_DATASET, OneClientTestCase1.ONE_CLIENT_DATASET )

        sleep( 2 )  # Wait for the receiver to initialize.
        w.training( self.ig_port )
        w.evaluate()
