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
import logging
import grpc
import pdb
import os
import struct
import sys

######### PTF modules for BFRuntime Client Library APIs #######
import ptf
from ptf.testutils import *
from bfruntime_client_base_tests import BfRuntimeTest
import bfrt_grpc.bfruntime_pb2 as bfruntime_pb2
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
    def setUp( self, tableSetUp = None ) -> None:
        p4_program_test.P4ProgramTest.setUp( self, self.tableSetUp )

        self.pre_node = self.bfrt_info.table_get( '$pre.node' )
        self.pre_mgid = self.bfrt_info.table_get( '$pre.mgid' )

    def tableSetUp( self ) -> None:
        # Since this class is not a test per se, we can use the setup method
        # for common setup. For example, we can have our tables and annotations ready
        pass

#
# Individual tests can now be subclassed from BaseProgramTest
#
