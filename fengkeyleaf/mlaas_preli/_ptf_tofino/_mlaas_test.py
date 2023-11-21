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

import random
from typing import List

# scapy imports
from scapy.packet import Packet

# ptf imports
import ptf.testutils as tu



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
from fengkeyleaf import mlaas_pkt_tofino

__version__ = "1.0"


class BasicTestGroup( _mlaas_preli.MlaasBaseProgramTest ):
    pass

    # https://stackoverflow.com/a/805082
    # def runTest( self ) -> None:
    #     self._multicast_group_setup()


@tu.disabled
class MlaasPreliTest1host1PktCase1( BasicTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 5, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 5, 1 )
        tu.verify_packets( self, exp_pkt, self.rec_verify_ports )
        

@tu.disabled
class MlaasPreliTest1host1PktCase2( BasicTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -5, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -5, 1 )
        tu.verify_packets( self, exp_pkt, self.rec_verify_ports )


@tu.disabled
class MlaasPreliTest1hostCase1( BasicTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 5, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 5, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 10, 2 )
        tu.verify_packets( self, exp_pkt, self.rec_verify_ports )


@tu.disabled
class MlaasPreliTest1hostCase2( BasicTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 100, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 100000, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 100100, 2 )
        tu.verify_packets( self, exp_pkt, self.rec_verify_ports )


@tu.disabled
class MlaasPreliTest1hostCase3( BasicTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -5, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -15, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -20, 2 )
        tu.verify_packets( self, exp_pkt, self.rec_verify_ports )


@tu.disabled
class MlaasPreliTest1hostCase4( BasicTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -1000000, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -10000000, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -11000000, 2 )
        tu.verify_packets( self, exp_pkt, self.rec_verify_ports )


@tu.disabled
class MlaasPreliTest1hostCase5( BasicTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 10, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -5, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 5, 2 )
        tu.verify_packets( self, exp_pkt, self.rec_verify_ports )


@tu.disabled
class MlaasPreliTest1hostCase6( BasicTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -1000000, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 50,  0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -1000000 + 50, 2 )
        tu.verify_packets( self, exp_pkt, self.rec_verify_ports )


@tu.disabled
class MlaasPreliTest2hostCase1( BasicTestGroup ):
    def runTest( self ) -> None:
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, -10, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 1, 50, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip2, 0, 30,  0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip2, 1, -60, 0 )

        tu.send_packet( self, self.eg_port, pkt1 )
        exp_pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip2, 0, 20, 2 )
        tu.verify_packets( self, exp_pkt1, self.rec_verify_ports )

        tu.send_packet( self, self.eg_port, pkt2 )
        exp_pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip2, 1, -10, 2 )
        tu.verify_packets( self, exp_pkt2, self.rec_verify_ports )


@tu.disabled
class MlaasPreliTest2hostRandom( BasicTestGroup ):
    POOL_SIZE: int = 256
    EXP: int = 16
    MAX_INT: int = 2 ** EXP - 1
    MIN_INT: int = -( 2 ** EXP )

    # TODO: Sacling factor

    def training( self, n_workers: int ) -> None:
        idx: int = random.randint( 0, MlaasPreliTest2hostRandom.POOL_SIZE - 1 )
        G: List[ int ] = [
            random.randint( MlaasPreliTest2hostRandom.MIN_INT, MlaasPreliTest2hostRandom.MAX_INT )
            for _ in range( n_workers )
        ]
        s: int = sum( G )

        # TODO: random ig_port
        for g in G:
            pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, idx, g, 0 )
            tu.send_packet( self, self.ig_port, pkt )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, idx, s, n_workers )
        tu.verify_packets( self, exp_pkt, self.rec_verify_ports )

        # TODO: Convert to int when verifying.

    MAX_EPOCHES: int = 10000

    def runTest( self ) -> None:
        self._multicast_group_setup()

        n_epochs: int = 1
        n_epochs = MlaasPreliTest2hostRandom.MAX_EPOCHES
        n_workers: int = 16

        for _ in range( n_epochs ):
            self.training( n_workers )
