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

import _mlaas_preli

from fengkeyleaf.logging import my_logging

__version__ = "1.0"


# This new Base Class extends the setup method of Simple L3 by adding the
# desired network setup
class TestGroup1( _mlaas_preli.BasicForwardingBaseProgramTest ):
    IP_1: str = "10.0.1.1"
    IP_2: str = "10.0.2.2"

    def __init__( self ):
        super().__init__()

        self.l: logging = my_logging.get_logger( logging.INFO )

    def setUp( self, tableSetUp = None ):
        _mlaas_preli.BasicForwardingBaseProgramTest.setUp( self )

        # Program 3 entries in ipv4_lpm
        self.programTable(
            self.ipv4_lpm,
            [
                # ipv4_lpm.add_with_send("10.0.1.1", 32, 1)
                (
                    # Key
                    [ ( "hdr.ipv4.dstAddr", TestGroup1.IP_1, None, 32 ) ],
                    # Action
                    "Ingress.send",
                    # Action params
                    [ ( "port", self.swports[ 1 ] ) ]
                ),
                # ipv4_lpm.add_with_send("10.0.2.2", 28, 2)
                (
                    [ ( "hdr.ipv4.dstAddr", TestGroup1.IP_2, None, 28 ) ],
                    "Ingress.send",
                    [ ( "port", self.swports[ 2 ] ) ]
                )
            ]
        )

    def test( self, ip: str, egress_port: int ) -> None:
        # Test Parameters
        ingress_port = self.swports[ 0 ]

        self.l.info( "Sending packet with IPv4 DST ADDR=%s into port %d" % ( ip, ingress_port ) )
        pkt: Packet = tu.simple_tcp_packet(
            eth_dst = "00:98:76:54:32:10",
            eth_src = '00:55:55:55:55:55',
            ip_dst = ip,
            ip_id = 101,
            ip_ttl = 64,
            ip_ihl = 5
        )

        tu.send_packet( self, ingress_port, pkt )
        self.l.info( "Expecting the packet to be forwarded to port %d" % egress_port )
        tu.verify_packet( self, pkt, egress_port )
        self.l.info( "Packet received of port %d" % egress_port )


#
# The following are multiple tests that all use the same setup
#
# There are a lot of tests that can be run on this topology. Feel free to
# add more
#

class Test1_1( TestGroup1 ):
    """
    Sending a packet to 10.0.1.1 into port 0. Expected on Port 1
    """
    def runTest( self ):
        self.test( Test1_1.IP_1, self.swports[ 1 ] )


class Test1_2( TestGroup1 ):
    """
    Sending a packet to 10.0.2.2 into port 0. Expected on Port 2
    """

    def runTest( self ):
        self.test( Test1_1.IP_2, self.swports[ 2 ] )
