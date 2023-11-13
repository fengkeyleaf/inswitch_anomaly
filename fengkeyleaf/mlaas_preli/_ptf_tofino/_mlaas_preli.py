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

    def tableSetUp( self ):
        # Since this class is not a test per se, we can use the setup method
        # for common setup. For example, we can have our tables and annotations
        # ready
        self.ipv4_lpm = self.bfrt_info.table_get( "Ingress.ipv4_lpm" )
        self.ipv4_lpm.info.key_field_annotation_add( "hdr.ipv4.dst_addr", "ipv4" )

        self.tables = [ self.ipv4_lpm ]

#
# Individual tests can now be subclassed from BaseProgramTest
#
