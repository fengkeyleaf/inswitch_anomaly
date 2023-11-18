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
import logging

# scapy imports
from scapy.layers.inet import IP, Ether
from scapy.packet import Packet

# ptf imports
import ptf.testutils as tu

# bfrt imports
import bfrt_grpc.client as gc

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


class TestGroup1( _mlaas_preli.MlaasBaseProgramTest ):

    def __init__( self ):
        super().__init__()

        self.ig_port: int =  1
        self.eg_port: int =  2
        self.in_smac: str = '08:00:00:00:01:11'
        self.in_dmac: str = '08:00:00:00:02:22'
        self.ip1: str = "10.0.1.1"
        self.ip2: str = "10.0.2.2"

    def _multicast_group_setup( self ) -> None:
        # Create the multicast nodes
        # Corresponding bfrt code
        # bfrt.pre.node.entry(
        #     MULTICAST_NODE_ID = 105, MULTICAST_RID = 5,
        #     MULTICAST_LAG_ID = [], DEV_PORT = [ 1, 2 ]
        # ).push()

        # Ptf code
        no_mod_node_id: int = tu.test_param_get( "no_mod_node_id", 105 )
        no_mod_rid: int = tu.test_param_get( "no_mod_rid", 5 )
        no_mod_ports: List[ int ] = [ self.swports[ p ] for p in tu.test_param_get( "no_mod_ports", [ 1, 2 ] ) ]
        print( type( no_mod_ports ) )
        no_mod_key = self.pre_node.make_key( [ gc.KeyTuple( "$MULTICAST_NODE_ID", no_mod_node_id ) ] )
        print( type( no_mod_key ) )

        no_mod_data = self.pre_node.make_data( [
            gc.DataTuple( '$MULTICAST_RID', no_mod_rid ),
            gc.DataTuple( '$DEV_PORT', int_arr_val = no_mod_ports )
        ] )

        self.pre_node.entry_add( self.dev_tgt, [ no_mod_key ], [ no_mod_data ] )
        self.l.info( "Added No Mods PRE Node ({}) --> ports {}".format( no_mod_node_id, no_mod_ports ) )

        # Create the multicast group
        # Corresponding bfrt code
        # bfrt.pre.mgid.entry(
        #     MGID = 1,
        #     MULTICAST_NODE_ID = [ 3 ],
        #     MULTICAST_NODE_L1_XID_VALID = [ False ],
        #     MULTICAST_NODE_L1_XID = [ 0 ]
        # ).push()

        # pft code
        mgrp_id = tu.test_param_get( "mgrp_id",  1 )
        key = self.pre_mgid.make_key( [ gc.KeyTuple( '$MGID', mgrp_id ) ] )
        data = self.pre_mgid.make_data(
            [
                gc.DataTuple( '$MULTICAST_NODE_ID', int_arr_val = [  no_mod_node_id ] ),
                gc.DataTuple( '$MULTICAST_NODE_L1_XID_VALID', bool_arr_val = [ False ] ),
                gc.DataTuple( '$MULTICAST_NODE_L1_XID', int_arr_val = [ 0 ] )
            ]
        )

        self.pre_mgid.entry_add( self.dev_tgt, [ key ], [ data ] )
        self.l.info( 'Added MGID {} with nodes {}'.format( mgrp_id, [ no_mod_node_id ] ) )


# @tu.disabled
class MlaasPreliTest1host1PktCase1( TestGroup1 ):
    def runTest( self ):
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 5,  0 )
        tu.send_packet( self, self.ig_port, pkt1 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 0, 5,  1 )
        tu.verify_packets( self, exp_pkt, [ self.eg_port ] )
        

@tu.disabled
class MlaasPreliTest1host1PktCase2( TestGroup1 ):
    def runTest( self ):
        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, -5, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, -5, 1 )
        tu.verify_packets( self, exp_pkt, [ self.eg_port ] )


@tu.disabled
class MlaasPreliTest1hostCase1( TestGroup1 ):
    def runTest( self ):        
        self._multicast_group_setup()

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 5,  0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 5,  0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 10,  2 )
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


@tu.disabled
class MlaasPreliTest1hostCase2( TestGroup1 ):
    def runTest( self ):
        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 100, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 100000, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, 100100, 2 )
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


@tu.disabled
class MlaasPreliTest1hostCase3( TestGroup1 ):
    def runTest( self ):
        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, -5, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, -15,0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, -20, 2 )
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


@tu.disabled
class MlaasPreliTest1hostCase4( TestGroup1 ):
    def runTest( self ):
        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, -1000000,0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, -10000000,0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, -11000000, 2 )
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


@tu.disabled
class MlaasPreliTest1hostCase5( TestGroup1 ):
    def runTest( self ):
        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 10,0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, -5, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, 5,2 )
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


@tu.disabled
class MlaasPreliTest1hostCase6( TestGroup1 ):
    def runTest( self ):
        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, -1000000, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 50,  0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, -1000000 + 50, 2 )
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


@tu.disabled
class MlaasPreliTest2hostCase1( TestGroup1 ):
    def runTest( self ):
        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, -10, 0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 1, 50, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip2, 64, 0, 30,  0 )
        pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip2, 64, 1, -40, 0 )

        tu.send_packet( self, self.eg_port, pkt1 )
        exp_pkt1: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip2, 64, 0, 20, 2 )
        tu.verify_packets( self, exp_pkt1, [ self.eg_port ] )

        tu.send_packet( self, self.eg_port, pkt2 )
        exp_pkt2: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip2, 64, 1, 10, 2 )
        tu.verify_packets( self, exp_pkt2, [ self.eg_port ] )


@tu.disabled
class MlaasPreliTest2hostRandom( TestGroup1 ):
    POOL_SIZE: int = 256
    EXP: int = 16
    MAX_INT: int = 2 ** EXP - 1
    MIN_INT: int = -(2 ** EXP)

    # Sacling factor

    @staticmethod
    def convert_to_pkt( g: int ):
        pos: int = 0
        neg: int = 0
        sign: bool = False  # Positive

        if g < 0:
            sign = True
            neg = abs( g )
        else:
            pos = g

        return (pos, neg, sign)

    def training( self, n_workers: int ):
        idx: int = random.randint( 0, MlaasPreliTest2hostRandom.POOL_SIZE - 1 )
        G: List[ int ] = [
            random.randint( MlaasPreliTest2hostRandom.MIN_INT, MlaasPreliTest2hostRandom.MAX_INT )
            for _ in range( n_workers )
        ]
        s: int = sum( G )

        s_pos: int = 0
        s_neg: int = 0
        # TODO: random ig_port
        # TODO: boardcase updates
        for g in G:
            (pos, neg, sign) = MlaasPreliTest2hostRandom.convert_to_pkt( g )
            s_pos += pos
            s_neg += neg
            pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_smac, self.in_dmac, self.ip1, 64, idx, pos, neg, sign, 0 )
            tu.send_packet( self, self.ig_port, pkt )

        exp_pkt: Packet = mlaas_pkt_tofino.get_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, idx, s_pos, s_neg, False, n_workers )
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )

        # TODO: Convert to int when verifying.

    def runTest( self ):
        n_epochs: int = 10000
        n_workers: int = 16

        for _ in range( n_epochs ):
            self.training( n_workers )
