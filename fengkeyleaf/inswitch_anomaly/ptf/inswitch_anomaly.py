# -*- coding: utf-8 -*-

import logging
from typing import Any

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

from fengkeyleaf import my_logging

__version__ = "1.0"


l: logging = my_logging.get_logger( logging.DEBUG )


# Test baseclass
# https://github.com/jafingerhut/p4-guide/blob/master/demo1/ptf/demo1.py
class PtfTest( BaseTest ):
    TEST_NAME: str = "inswtich_anomaly"

    def setUp( self ) -> None:
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

    def tearDown( self ) -> None:
        l.debug( "PTF_Test( " + PtfTest.TEST_NAME + " ).tearDown()" )
        sh.teardown()

# https://github.com/p4lang/p4runtime-shell
# Set a field value with <self>['<field_name>'] = '...'
#   * For exact match: <self>['<f>'] = '<value>'
#   * For ternary match: <self>['<f>'] = '<value>&&&<mask>'
#   * For LPM match: <self>['<f>'] = '<value>/<mask>'
#   * For range match: <self>['<f>'] = '<value>..<mask>'
#   * For optional match: <self>['<f>'] = '<value>'


class _InswtichAnomalyTestBasee( PtfTest ):
    IP_ADDR_1: str = "192.168.100.1"
    IP_ADDR_2: str = "192.168.100.3"

    @staticmethod
    def _add_feature_rules(
            t: str, a: str, m_n: str, m_v: str, p_n: str, p_v: Any
    ) -> None:
        te = sh.TableEntry( t )( action = a )
        te.match[ m_n ] = m_v
        te.action[ p_n ] = p_v
        te.insert()


# Test cases
class _InswtichAnomalyTest( _InswtichAnomalyTestBasee ):

    @staticmethod
    def _add_actions() -> None:
        te = sh.TableEntry( "MyIngress.decision_tree" )( action = "MyIngress.drop" )
        te.match[ "meta.src_count_select" ] = "1..1"
        te.match[ "meta.src_tls_select" ] = "1..1"
        te.match[ "meta.dst_count_select" ] = "1..2"
        te.match[ "meta.dst_tls_select" ] = "1..1"
        te.insert()

        te = sh.TableEntry( "MyIngress.decision_tree" )( action = "MyIngress.ipv4_forward" )
        te.match[ "meta.src_count_select" ] = "1..1"
        te.match[ "meta.src_tls_select" ] = "1..1"
        te.match[ "meta.dst_count_select" ] = "3..4"
        te.match[ "meta.dst_tls_select" ] = "1..1"
        te.action[ "dstAddr" ] = "08:00:00:00:01:11"
        te.action[ "port" ] = "1"
        te.insert()

    @staticmethod
    def _add_rules() -> None:
        _InswtichAnomalyTest._add_actions()

        _InswtichAnomalyTest._add_feature_rules( "Sketch.src_count_select_t", "Sketch.src_count_select_a", "scv", "0..32", "v", 1 )
        _InswtichAnomalyTest._add_feature_rules( "Sketch.src_tls_select_t", "Sketch.src_tls_select_a", "stv", "0..1", "v", 1 )
        _InswtichAnomalyTest._add_feature_rules( "Sketch.dst_count_select_t", "Sketch.dst_count_select_a", "dcv", "1..5000", "v", 2 )

    def runtTest( self ) -> None:
        l.info( "Testing with the dataset of 10 pkts" )
        ig_port: int = 2 # Host to send pkts.
        eg_port: int = 1 # Host to receive good pkts.

        # Before adding any table entries, the default behavior for
        # sending in an IPv4 packet is to drop it.
        pkt: scapy.packet.Packet = tu.simple_ip_packet(
            ip_src = _InswtichAnomalyTest.IP_ADDR_1,
            ip_dst = _InswtichAnomalyTest.IP_ADDR_2
        )
        tu.send_packet( self, ig_port, pkt )
        tu.verify_no_other_packets( self )

        _InswtichAnomalyTest._add_rules()

        tu.send_packet( self, ig_port, pkt )
        tu.verify_packets( self, pkt, [ eg_port ] )

