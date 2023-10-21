# -*- coding: utf-8 -*-

import logging
import sys
import os

# scapy imports
import scapy.packet
# ptf imports
import ptf
import ptf.testutils as tu
from ptf.base_tests import BaseTest
# p4runtime imports
import p4runtime_sh.shell as sh

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# fengkeyleaf imports
# Add path dependency
sys.path.append(
    os.path.join(
        os.path.dirname( os.path.abspath(__file__) ),
        '../../../'
    )
)
# Import packages
from fengkeyleaf.logging import my_logging

__version__ = "1.0"

# PTF commands
# Compile
# p4c --target bmv2 --arch v1model -o ./build/ --p4runtime-files ./build/inswitch_anomaly.p4info.txt ./inswitch_anomaly.p4

# Add virtual network interfaces
# sudo ./tools/veth_setup.sh

# Start the switch.
# sudo simple_switch_grpc \
#      --log-console \
#      --log-flush \
#      --dump-packet-data 10000 \
#      -i 0@veth0 \
#      -i 1@veth2 \
#      -i 2@veth4 \
#      -i 3@veth6 \
#      -i 4@veth8 \
#      -i 5@veth10 \
#      -i 6@veth12 \
#      -i 7@veth14 \
#      --no-p4

# Start CLI
# simple_switch_CLI

# Start PTF
# sudo `which ptf`\
#     -i 0@veth1 \
#     -i 1@veth3 \
#     -i 2@veth5 \
#     -i 3@veth7 \
#     -i 4@veth9 \
#     -i 5@veth11 \
#     -i 6@veth13 \
#     -i 7@veth15 \
#     --test-params="grpcaddr='localhost:9559';p4info='./build/inswitch_anomaly.p4info.txt';config='./build/inswitch_anomaly.json'" \
#     --test-dir ./fengkeyleaf/inswitch_anomaly/ptf


l: logging = my_logging.get_logger( logging.DEBUG )


# Test baseclass
# https://github.com/jafingerhut/p4-guide/blob/master/demo1/ptf/demo1.py
class PtfTest( BaseTest ):
    TEST_NAME: str = "inswtich_anomaly"

    def setUp( self ):
        # Setting up PTF dataplane
        self.dataplane = ptf.dataplane_instance
        self.dataplane.flush()

        l.debug( "PTF_Test( " + PtfTest.TEST_NAME + " ).setUp()" )
        grpc_addr: str = tu.test_param_get( "grpcaddr" )
        if grpc_addr is None:
            grpc_addr = 'localhost:9559'
        p4info_txt_fname: str = tu.test_param_get( "p4info" )
        p4prog_binary_fname: str = tu.test_param_get( "config" )
        # print( p4info_txt_fname )
        # print( p4prog_binary_fname )
        sh.setup(
            device_id = 0,
            grpc_addr = grpc_addr,
            election_id = ( 0, 1 ), # (high_32bits, lo_32bits)
            config = sh.FwdPipeConfig( p4info_txt_fname, p4prog_binary_fname )
        )
        #p4rtutil.dump_table("ipv4_da_lpm")
        #p4rtutil.dump_table("mac_da")
        #p4rtutil.dump_table("send_frame")

    def tearDown( self ):
        l.debug( "PTF_Test( " + PtfTest.TEST_NAME + " ).tearDown()" )
        sh.teardown()

# https://github.com/p4lang/p4runtime-shell
# Set a field value with <self>['<field_name>'] = '...'
#   * For exact match: <self>['<f>'] = '<value>'
#   * For ternary match: <self>['<f>'] = '<value>&&&<mask>'
#   * For LPM match: <self>['<f>'] = '<value>/<mask>'
#   * For range match: <self>['<f>'] = '<value>..<mask>'
#   * For optional match: <self>['<f>'] = '<value>'


class InswtichAnomalyTestBasee( PtfTest ):
    IP_ADDR_1: str = "192.168.100.1"
    IP_ADDR_2: str = "192.168.100.3"

    # Action parameter value must be a string
    @staticmethod
    def _add_feature_rules(
            t: str, a: str, m_n: str, m_v: str, p_n: str, p_v: str
    ) -> None:
        te = sh.TableEntry( t )( action = a )
        te.match[ m_n ] = m_v
        te.action[ p_n ] = p_v
        te.priority = 1
        te.insert()


# Test cases
class InswtichAnomalyTest( InswtichAnomalyTestBasee ):

    @staticmethod
    def _add_actions() -> None:
        te = sh.TableEntry( "MyIngress.decision_tree" )( action = "MyIngress.drop" )
        te.match[ "meta.src_count_select" ] = "1..1"
        te.match[ "meta.src_tls_select" ] = "1..1"
        te.match[ "meta.dst_count_select" ] = "1..2"
        te.match[ "meta.dst_tls_select" ] = "1..1"
        te.priority = 1
        te.insert()

        te = sh.TableEntry( "MyIngress.decision_tree" )( action = "MyIngress.ipv4_forward" )
        te.match[ "meta.src_count_select" ] = "1..1"
        te.match[ "meta.src_tls_select" ] = "1..1"
        te.match[ "meta.dst_count_select" ] = "3..4"
        te.match[ "meta.dst_tls_select" ] = "1..1"
        te.action[ "dstAddr" ] = "08:00:00:00:01:11"
        te.action[ "port" ] = "1"
        te.priority = 1
        te.insert()

    @staticmethod
    def _add_rules() -> None:
        InswtichAnomalyTest._add_actions()

        InswtichAnomalyTest._add_feature_rules( "MyIngress.s.src_count_select_t", "MyIngress.s.src_count_select_a", "scv", "0..32", "v", "1" )
        InswtichAnomalyTest._add_feature_rules( "MyIngress.s.src_tls_select_t", "MyIngress.s.src_tls_select_a", "stv", "0..1", "v", "1" )
        InswtichAnomalyTest._add_feature_rules( "MyIngress.s.dst_count_select_t", "MyIngress.s.dst_count_select_a", "dcv", "1..5000", "v", "2" )

    def runTest( self ):
        l.info( "Testing with the dataset of 10 pkts" )
        ig_port: int = 2 # Host to send pkts.
        eg_port: int = 1 # Host to receive good pkts.

        # Before adding any table entries, the default behavior for
        # sending in an IPv4 packet is to drop it.
        pkt: scapy.packet.Packet = tu.simple_ip_packet(
            ip_src = InswtichAnomalyTest.IP_ADDR_1,
            ip_dst = InswtichAnomalyTest.IP_ADDR_2
        )
        # tu.send_packet( self, ig_port, pkt )
        # tu.verify_no_other_packets( self )

        InswtichAnomalyTest._add_rules()

        tu.send_packet( self, ig_port, pkt )
        tu.verify_packets( self, pkt, [ eg_port ] )

