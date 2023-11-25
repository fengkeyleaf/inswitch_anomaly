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

# Called by a program from the working directory.
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
    LR: float = 0.001

    # Using absolute path here.
    # Replace with your file paths before running the ptf test.

    # One client
    # Full dataset
    FULL_DATASET: str = "/root/inswitch_anomaly/inswitch_anomaly/fengkeyleaf/other/neural_network/pima-indians-diabetes.data.csv"
    # Partial dataset
    ONE_CLIENT_DATASET: str = "/root/inswitch_anomaly/inswitch_anomaly/fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_small.csv"
    
    # Two clients
    # Both have partial data sets.
    # Equal size, small
    TWO_CLIENT_SMALL_EQUAL_DATASET1: str = "/root/inswitch_anomaly/inswitch_anomaly/fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/small/pima-indians-diabetes.data_part1.csv"
    TWO_CLIENT_SMALL_EQUAL_DATASET2: str = "/root/inswitch_anomaly/inswitch_anomaly/fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/small/pima-indians-diabetes.data_part2.csv"
    # Normal
    # f1: str = "/root/inswitch_anomaly/inswitch_anomaly/fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/pima-indians-diabetes.data_part1.csv"
    # f2: str = "/root/inswitch_anomaly/inswitch_anomaly/fengkeyleaf/mlaas_preli/test_data/two_clients_equal_size/pima-indians-diabetes.data_part2.csv"
    # Inequal size
    # f = "fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_part1.csv"
    # f = "fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data_part2.csv"
    
    @staticmethod
    def init_worker( tf: str, vf: str, p: int ) -> woker_tofino.Worker:
        w: woker_tofino.Worker = woker_tofino.Worker( OneClientTestCase1.LR, logging.INFO )
        w.config_receiver( p )
        w.build_model()
        w.load_data( OneClientTestCase1.FULL_DATASET, OneClientTestCase1.FULL_DATASET )

        sleep( woker_tofino.Worker.SETUP_WAITING_TIME )  # Wait for the receiver to initialize.
        return w


# @tu.disabled
class OneClientTestCase1( WorkerTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        w: woker_tofino.Worker = woker_tofino.Worker( OneClientTestCase1.LR, logging.INFO )
        w.config_receiver( self.ig_port )
        w.build_model()
        w.load_data( OneClientTestCase1.FULL_DATASET, OneClientTestCase1.FULL_DATASET )

        sleep( woker_tofino.Worker.SETUP_WAITING_TIME )  # Wait for the receiver to initialize.
        w.training( self.ig_port )
        w.evaluate()


class TwoClientsTestCase2( WorkerTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        w1: woker_tofino.Worker = TwoClientsTestCase2.init_worker(
            TwoClientsTestCase2.TWO_CLIENT_SMALL_EQUAL_DATASET1, TwoClientsTestCase2.FULL_DATASET,
            self.ig_port
        )
        w1.set_sen_port( self.ig_port )
        w1.start()

        sleep( woker_tofino.Worker.SETUP_WAITING_TIME )

        w2: woker_tofino.Worker = TwoClientsTestCase2.init_worker(
            TwoClientsTestCase2.TWO_CLIENT_SMALL_EQUAL_DATASET1, TwoClientsTestCase2.FULL_DATASET,
            self.eg_port
        )
        w2.set_sen_port( self.eg_port )
        w2.start()

