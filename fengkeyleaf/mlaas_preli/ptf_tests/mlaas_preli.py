# -*- coding: utf-8 -*-

import logging
from scapy.all import IP, Ether, Packet
import ptf
import ptf.testutils as tu
from ptf.base_tests import BaseTest
import p4runtime_sh.shell as sh
# import p4runtime_shell_utils as p4rtutil

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com

"""

import mlaas_pkt

# p4c --target bmv2 --arch v1model -o ./build/ --p4runtime-files ./build/mlaas_preli.p4info.txt ./mlaas_preli.p4

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

# simple_switch_CLI

# sudo `which ptf`\
#     -i 0@veth1 \
#     -i 1@veth3 \
#     -i 2@veth5 \
#     -i 3@veth7 \
#     -i 4@veth9 \
#     -i 5@veth11 \
#     -i 6@veth13 \
#     -i 7@veth15 \
#     --test-params="grpcaddr='localhost:9559';p4info='./build/mlaas_preli.p4info.txt';config='./build/mlaas_preli.json'" \
#     --test-dir ./fengkeyleaf/mlaas_preli/ptf_tests

# The effect achieved by the code below seems to be that many DEBUG
# and higher priority logging messages go to the console, and also to
# a file named 'ptf.log'.  Some of the messages written to the
# 'ptf.log' file do not go to the console, and appear to be created
# from within the ptf library.

logger = logging.getLogger(None)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


# https://github.com/jafingerhut/p4-guide/blob/master/demo1/ptf/demo1.py
class PTF_Test( BaseTest ):
    def setUp(self):
        # Setting up PTF dataplane
        self.dataplane = ptf.dataplane_instance
        self.dataplane.flush()

        logging.debug( "PTF_Test( mlaas_preli ).setUp()" )
        grpc_addr: str = tu.test_param_get( "grpcaddr" )
        if grpc_addr is None:
            grpc_addr = 'localhost:9559'
        p4info_txt_fname: str = tu.test_param_get( "p4info" )
        p4prog_binary_fname: str = tu.test_param_get( "config" )
        # print( p4info_txt_fname )
        # print( p4prog_binary_fname )
        sh.setup(
            device_id=0,
            grpc_addr=grpc_addr,
            election_id=(0, 1), # (high_32bits, lo_32bits)
            config=sh.FwdPipeConfig(p4info_txt_fname, p4prog_binary_fname)
        )
        #p4rtutil.dump_table("ipv4_da_lpm")
        #p4rtutil.dump_table("mac_da")
        #p4rtutil.dump_table("send_frame")

    def tearDown( self ):
        logging.debug( "PTF_Test( mlaas_preli ).tearDown()" )
        sh.teardown()


@tu.disabled
class Ipv4_lpm_Test( PTF_Test ):
    @staticmethod
    def add_rules_ipv4_lpm():
         # table_set_default MyIngress.ipv4_lpm MyIngress.drop
        te: sh.TableEntry = sh.TableEntry( "MyIngress.ipv4_lpm" )( action = "MyIngress.drop", is_default = True )
        te.modify()
    
        # table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.1.1/32 => 08:00:00:00:01:11 1
        te = sh.TableEntry( "MyIngress.ipv4_lpm" )( action = "MyIngress.ipv4_forward" )
        te.match[ "hdr.ipv4.dstAddr" ] = "10.0.1.1/32"
        te.action[ "dstAddr" ] = "08:00:00:00:01:11"
        te.action[ "port" ] = "1"
        te.insert()

        # table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.2.2/32 => 08:00:00:00:02:22 2
        te = sh.TableEntry( "MyIngress.ipv4_lpm" )( action = "MyIngress.ipv4_forward" )
        te.match[ "hdr.ipv4.dstAddr" ] = "10.0.2.2/32"
        te.action[ "dstAddr" ] = "08:00:00:00:02:22"
        te.action[ "port" ] = "2"
        te.insert()

    def runTest( self ):
        print( "Sending a TCP packet port 1 -> port 2)" )
        ig_port: int = 1
        eg_port: int = 2
        in_smac: str = '08:00:00:00:01:11'
        in_dmac: str = '08:00:00:00:02:22'
        ip1: str = "10.0.1.1"
        ip2: str = "10.0.2.2"
        
        # Before adding any table entries, the default behavior for
        # sending in an IPv4 packet is to drop it.
        pkt: Packet = tu.simple_tcp_packet( 
            eth_src = in_smac, eth_dst = in_dmac, ip_src = ip1,
            ip_dst = ip2, ip_ttl = 64 
        )
        tu.send_packet( self, ig_port, pkt )
        tu.verify_no_other_packets( self )

        Ipv4_lpm_Test.add_rules_ipv4_lpm()

        # Check that the entry is hit, expected source and dest MAC
        # have been written into output packet, TTL has been
        # decremented, and that no other packets are received.
        exp_pkt: Packet = tu.simple_tcp_packet( 
            eth_src = in_dmac, eth_dst = in_dmac, ip_src = ip1,
            ip_dst = ip2, ip_ttl = 63 
        )
        tu.send_packet( self, ig_port, pkt )
        tu.verify_packets( self, exp_pkt, [ eg_port ] )


def get_mlaas_pkt( 
        src_mac: str, dst_mac: str, addr, ttl: int,
        idx: int, gradPos: int, gradNeg: int, sign: bool, number_of_worker: int
) -> Packet:
    pkt =  Ether(src = src_mac, dst = dst_mac)
    pkt = pkt / IP( dst = addr, ttl = ttl ) / mlaas_pkt.Mlaas_p( 
        idx = idx, gradPos = gradPos, gradNeg = gradNeg, 
        sign = sign, reserves = 0, numberOfWorker = number_of_worker
    )
    # pkt.show2()
    return pkt


# Cannot be disabled.
class Mlass_preli_test( PTF_Test ):
    def __init__( self, methodName: str = "runTest" ) -> None:
        super().__init__( methodName )

        self.ig_port: int = 1
        self.eg_port: int = 2
        self.in_smac: str = '08:00:00:00:01:11'
        self.in_dmac: str = '08:00:00:00:02:22'
        self.ip1: str = "10.0.1.1"
        self.ip2: str = "10.0.2.2"


# ptf--test-dir ./fengkeyleaf/mlaas_preli/ptf_tests --list
@tu.disabled
class Mlaas_preli_test_1host_case1( Mlass_preli_test ):
    def runTest( self ):
        pkt1: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 5, 0, False, 0 )
        pkt2: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 5, 0, False, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, 10, 0, False, 2 );
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


# @tu.disabled
class Mlaas_preli_test_1host_case2( Mlass_preli_test ):
    def runTest( self ):
        pkt1: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 100, 0, False, 0 )
        pkt2: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 100000, 0, False, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, 100100, 0, False, 2 );
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


# @tu.disabled
class Mlaas_preli_test_1host_case3( Mlass_preli_test ):
    def runTest( self ):
        pkt1: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 0, 5, True, 0 )
        pkt2: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 0, 15, True, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, 0, 20, True, 2 );
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


# @tu.disabled
class Mlaas_preli_test_1host_case4( Mlass_preli_test ):
    def runTest( self ):
        pkt1: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 1, 1000000, True, 0 )
        pkt2: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 2, 10000000, True, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, 0, 11000000, True, 2 );
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


# @tu.disabled
class Mlaas_preli_test_1host_case5( Mlass_preli_test ):
    def runTest( self ):
        pkt1: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 10, 0, False, 0 )
        pkt2: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 0, 5, True, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, 10, 5, True, 2 );
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


# @tu.disabled
class Mlaas_preli_test_1host_case6( Mlass_preli_test ):
    def runTest( self ):
        pkt1: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 0, 1000000, True, 0 )
        pkt2: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 50, 0, False, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        exp_pkt: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip1, 63, 0, 50, 1000000, False, 2 );
        tu.verify_packets( self, exp_pkt, [ self.ig_port ] )


@tu.disabled
class Mlaas_preli_test_2host_case1( Mlass_preli_test ):
    def runTest( self ):
        pkt1: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 0, 0, 10, True, 0 )
        pkt2: Packet = get_mlaas_pkt( self.in_smac, self.in_dmac, self.ip1, 64, 1, 50, 0, False, 0 )
        tu.send_packet( self, self.ig_port, pkt1 )
        tu.send_packet( self, self.ig_port, pkt2 )

        pkt1: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip2, 64, 0, 30, 0, False, 0 )
        pkt2: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip2, 64, 1, 0, 40, True, 0 )

        tu.send_packet( self, self.eg_port, pkt1 )
        exp_pkt1: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip2, 63, 0, 30, 10, False, 2 );
        tu.verify_packets( self, exp_pkt1, [ self.eg_port ] )
        
        tu.send_packet( self, self.eg_port, pkt2 )
        exp_pkt2: Packet = get_mlaas_pkt( self.in_dmac, self.in_dmac, self.ip2, 63, 1, 50, 40, True, 2 );
        tu.verify_packets( self, exp_pkt2, [ self.eg_port ] )
