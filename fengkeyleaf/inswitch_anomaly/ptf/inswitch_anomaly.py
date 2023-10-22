# -*- coding: utf-8 -*-

import logging
import sys
import os

# scapy imports
import scapy.packet
from scapy.layers.inet import IP, Ether
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
# Add path dependency, which is allowed to exclude this file from the working directory.
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
    SCAPY_DST_FIELD_NAME: str = "dst"
    SCAPY_DEFAULT_TTL: int = 64

    MAX_SIGNED_INT: int = 0xffffff

    SKETCH_SRC_COUNT_TABLE_NAME: str = "MyIngress.s.src_count_select_t"
    SKETCH_SRC_COUNT_ACTION_NAME: str = "MyIngress.s.src_count_select_a"
    SKETCH_SRC_COUNT_PRARM_NAME: str = "scv"
    
    IG_PORT: int = 2 # Host to send pkts.
    EG_PORT: int = 1 # Host to receive good pkts.
    
    DST_MAC_ADDR: str = "08:00:00:00:01:11"
    IP_ADDR_1: str = "192.168.100.1"
    IP_ADDR_2: str = "192.168.100.3"
    PKT1: scapy.packet.Packet = tu.simple_ip_packet(
        ip_src = IP_ADDR_1,
        ip_dst = IP_ADDR_2
    )

    IP_ADDR_3: str = "192.168.100.7"
    IP_ADDR_4: str = "192.168.100.4"
    PKT2: scapy.packet.Packet = tu.simple_ip_packet(
        ip_src = IP_ADDR_3,
        ip_dst = IP_ADDR_4
    )

    IP_ADDR_5: str = "192.168.100.149"
    IP_ADDR_6: str = "27.124.125.250"
    PKT3: scapy.packet.Packet = tu.simple_ip_packet(
        ip_src = IP_ADDR_5,
        ip_dst = IP_ADDR_6
    )

    PKT4: scapy.packet.Packet = tu.simple_ip_packet(
        ip_src = IP_ADDR_4,
        ip_dst = IP_ADDR_3
    )

    IP_ADDR_7: str = "192.168.100.27"
    PKT5: scapy.packet.Packet = tu.simple_ip_packet(
        ip_src = IP_ADDR_7,
        ip_dst = IP_ADDR_1
    )

    IP_ADDR_8: str = "192.168.100.150"
    PKT6: scapy.packet.Packet = tu.simple_ip_packet(
        ip_src = IP_ADDR_8,
        ip_dst = IP_ADDR_2
    )

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

    # RANGE     00000000 -> 00000000
    @staticmethod
    def _add_actions() -> None:
        te = sh.TableEntry( "MyIngress.decision_tree" )( action = "MyIngress.drop" )
        te.match[ "meta.src_count_select" ] = "3..4"
        te.match[ "meta.src_tls_select" ] = "1..3"
        te.match[ "meta.dst_count_select" ] = "1..3"
        te.match[ "meta.dst_tls_select" ] = "1..3"
        te.priority = 1
        te.insert()

        te = sh.TableEntry( "MyIngress.decision_tree" )( action = "MyIngress.ipv4_forward" )
        te.match[ "meta.src_count_select" ] = "1..2"
        te.match[ "meta.src_tls_select" ] = "1..3"
        te.match[ "meta.dst_count_select" ] = "1..3"
        te.match[ "meta.dst_tls_select" ] = "1..3"
        te.action[ "dstAddr" ] = InswtichAnomalyTest.DST_MAC_ADDR
        te.action[ "port" ] = "1"
        te.priority = 1
        te.insert()

    @staticmethod
    def _add_rules() -> None:
        InswtichAnomalyTest._add_actions()

        InswtichAnomalyTest._add_feature_rules( 
            InswtichAnomalyTest.SKETCH_SRC_COUNT_TABLE_NAME,
            InswtichAnomalyTest.SKETCH_SRC_COUNT_ACTION_NAME,
            InswtichAnomalyTest.SKETCH_SRC_COUNT_PRARM_NAME, "0..2",
            "v", "1"
        )
        InswtichAnomalyTest._add_feature_rules( 
            InswtichAnomalyTest.SKETCH_SRC_COUNT_TABLE_NAME,
            InswtichAnomalyTest.SKETCH_SRC_COUNT_ACTION_NAME,
            InswtichAnomalyTest.SKETCH_SRC_COUNT_PRARM_NAME, "2.." + str( InswtichAnomalyTest.MAX_SIGNED_INT ), 
            "v", "2"
        )
        InswtichAnomalyTest._add_feature_rules( 
            "MyIngress.s.src_tls_select_t", 
            "MyIngress.s.src_tls_select_a", 
            "stv", "0..1000", "v", "1"
        )
        InswtichAnomalyTest._add_feature_rules( 
            "MyIngress.s.dst_count_select_t", 
            "MyIngress.s.dst_count_select_a", 
            "dcv", "0.." + str( InswtichAnomalyTest.MAX_SIGNED_INT ), "v", "1"
        )
        InswtichAnomalyTest._add_feature_rules( 
            "MyIngress.s.dst_tls_select_t", 
            "MyIngress.s.dst_tls_select_a", 
            "dtv", "0..1000", "v", "1"
        )

    def verify( self, p: scapy.packet.Packet, src: str, dst: str, is_rec: bool ) -> None:
        tu.send_packet( self, InswtichAnomalyTest.IG_PORT, p )

        exp_pkt: scapy.packet.Packet = tu.simple_ip_packet(
            eth_src = p[ Ether ].fields[ InswtichAnomalyTest.SCAPY_DST_FIELD_NAME ],
            eth_dst = InswtichAnomalyTest.DST_MAC_ADDR,
            ip_src = src,
            ip_dst = dst,
            ip_ttl = InswtichAnomalyTest.SCAPY_DEFAULT_TTL - 1 
        )

        if is_rec:
            tu.verify_packets( self, exp_pkt, [ InswtichAnomalyTest.EG_PORT ] )
            return

        tu.verify_no_other_packets( self )

    def runTest( self ):
        l.info( "Testing with the dataset of 10 pkts" )


        # Before adding any table entries, the default behavior for
        # sending in an IPv4 packet is to drop it.
        # tu.send_packet( self, ig_port, pkt )
        # tu.verify_no_other_packets( self )

        InswtichAnomalyTest._add_rules()

        # Good pkts. 
        # 1st pkt.
        # self.verify( InswtichAnomalyTest.PKT1, InswtichAnomalyTest.IP_ADDR_1, InswtichAnomalyTest.IP_ADDR_2, True )
        # 2nd pkt.
        self.verify( InswtichAnomalyTest.PKT2, InswtichAnomalyTest.IP_ADDR_3, InswtichAnomalyTest.IP_ADDR_4, True )
        # 3nd pkt.
        self.verify( InswtichAnomalyTest.PKT3, InswtichAnomalyTest.IP_ADDR_5, InswtichAnomalyTest.IP_ADDR_6, True )
        # 4th pkt.
        self.verify( InswtichAnomalyTest.PKT4, InswtichAnomalyTest.IP_ADDR_4, InswtichAnomalyTest.IP_ADDR_3, True )
        # 5th pkt.
        self.verify( InswtichAnomalyTest.PKT5, InswtichAnomalyTest.IP_ADDR_7, InswtichAnomalyTest.IP_ADDR_1, True )

        # Bad pkts.
        # 6th ~ 10th pkts.
        self.verify( InswtichAnomalyTest.PKT6, InswtichAnomalyTest.IP_ADDR_8, InswtichAnomalyTest.IP_ADDR_2, False )
        # self.verify( InswtichAnomalyTest.PKT6, InswtichAnomalyTest.IP_ADDR_8, InswtichAnomalyTest.IP_ADDR_2, False )