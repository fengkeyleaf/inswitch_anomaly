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

######### STANDARD MODULE IMPORTS ########
import os
from typing import List

######### PTF modules for BFRuntime Client Library APIs #######
# ptf imports
import ptf.testutils as tu
from ptf.testutils import *

# bfrt imports
import bfrt_grpc.client as gc

# Directly called from the working directory.
"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# fengkeyleaf imports
# Add path dependency, which is allowed to exclude this file from the working directory.
sys.path.append(
    os.path.join(
        os.path.dirname( os.path.abspath( __file__ ) ),
        '../../../'
    )
)
# Import packages
from fengkeyleaf.tofino import p4_program_test

__version__ = "1.0"


########## Program-specific Initialization ############
class BasicForwardingBaseProgramTest( p4_program_test.P4ProgramTest ):
    def setUp( self, tableSetUp = None ) -> None:
        p4_program_test.P4ProgramTest.setUp( self, self.tableSetUp )

    def tableSetUp( self ) -> None:
        # Since this class is not a test per se, we can use the setup method
        # for common setup. For example, we can have our tables and annotations
        # ready
        self.ipv4_lpm = self.bfrt_info.table_get( "Ingress.ipv4_lpm" )
        print( type( self.ipv4_lpm ) )
        self.ipv4_lpm.info.key_field_annotation_add( "hdr.ipv4.dstAddr", "ipv4" )

        self.tables = [ self.ipv4_lpm ]


class MlaasBaseProgramTest( p4_program_test.P4ProgramTest ):

    def __init__( self ) -> None:
        super().__init__()

        self.ig_port: int =  1
        self.eg_port: int =  2
        self.rec_verify_ports: List[ int ] = [ self.ig_port, self.eg_port ]
        self.in_smac: str = '08:00:00:00:01:11'
        self.in_dmac: str = '08:00:00:00:02:22'
        self.ip1: str = "10.0.1.1"
        self.ip2: str = "10.0.2.2"

    def setUp( self, tableSetUp = None ) -> None:
        p4_program_test.P4ProgramTest.setUp( self, self.tableSetUp )

        self.pre_node = self.bfrt_info.table_get( '$pre.node' )
        self.pre_mgid = self.bfrt_info.table_get( '$pre.mgid' )

    def tableSetUp( self ) -> None:
        # Since this class is not a test per se, we can use the setup method
        # for common setup. For example, we can have our tables and annotations ready
        pass

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

#
# Individual tests can now be subclassed from BaseProgramTest
#
