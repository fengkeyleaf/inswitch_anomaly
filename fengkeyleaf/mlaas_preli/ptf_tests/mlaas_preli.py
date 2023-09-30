# -*- coding: utf-8 -*-

import logging
from scapy.all import IP, Ether
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
#      --log-file ss-log \
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
class Demo1Test( BaseTest ):
    def setUp(self):
        # Setting up PTF dataplane
        self.dataplane = ptf.dataplane_instance
        self.dataplane.flush()

        logging.debug( "Demo1Test.setUp()" )
        grpc_addr = tu.test_param_get( "grpcaddr" )
        if grpc_addr is None:
            grpc_addr = 'localhost:9559'
        p4info_txt_fname = tu.test_param_get( "p4info" )
        p4prog_binary_fname = tu.test_param_get( "config" )
        print( p4info_txt_fname )
        print( p4prog_binary_fname )
        sh.setup(device_id=0,
                 grpc_addr=grpc_addr,
                 election_id=(0, 1), # (high_32bits, lo_32bits)
                 config=sh.FwdPipeConfig(p4info_txt_fname, p4prog_binary_fname)
                 )
        #p4rtutil.dump_table("ipv4_da_lpm")
        #p4rtutil.dump_table("mac_da")
        #p4rtutil.dump_table("send_frame")

    def tearDown( self ):
        logging.debug( "Demo1Test.tearDown()" )
        sh.teardown()


class Ipv4_lpm_Test( Demo1Test ):
    @staticmethod
    def add_rules_ipv4_lpm():
         # table_set_default MyIngress.ipv4_lpm MyIngress.drop
        te = sh.TableEntry( "MyIngress.ipv4_lpm" )( action = "MyIngress.drop", is_default = True )
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
        print( "Sending L2 packet port 1 -> port 2 [access vlan=10])" )
        ig_port = 1
        eg_port = 2
        in_smac = '08:00:00:00:01:11'
        in_dmac = '08:00:00:00:02:22'
        ip1: str = "10.0.1.1"
        ip2: str = "10.0.2.2"
        
        # Before adding any table entries, the default behavior for
        # sending in an IPv4 packet is to drop it.
        pkt = tu.simple_tcp_packet( eth_src = in_smac, eth_dst = in_dmac, ip_src = ip1,
                                    ip_dst = ip2, ip_ttl = 64 )
        tu.send_packet( self, ig_port, pkt )
        tu.verify_no_other_packets( self )

        Ipv4_lpm_Test.add_rules_ipv4_lpm()

        # Check that the entry is hit, expected source and dest MAC
        # have been written into output packet, TTL has been
        # decremented, and that no other packets are received.
        exp_pkt = tu.simple_tcp_packet( eth_src = in_dmac, eth_dst = in_dmac, ip_src = ip1,
                                       ip_dst = ip2, ip_ttl = 63 )
        tu.send_packet( self, ig_port, pkt )
        tu.verify_packets( self, exp_pkt, [ eg_port ] )
