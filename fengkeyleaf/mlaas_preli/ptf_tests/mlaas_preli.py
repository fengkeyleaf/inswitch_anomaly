# -*- coding: utf-8 -*-

from scapy.all import IP, Ether
from ptf.testutils import *

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com

"""

import sai_base_test
from switch_sai_thrift.ttypes import  *

import mlass_pkt

switch_inited=0
port_list = []
table_attr_list = []


def switch_init(client):
    global switch_inited
    if switch_inited:
        return

    switch_attr_list = client.sai_thrift_get_switch_attribute()
    attr_list = switch_attr_list.attr_list
    for attribute in attr_list:
        if attribute.id == 0:
            print ( "max ports: " + attribute.value.u32 )
        elif attribute.id == 1:
            for x in attribute.value.objlist.object_id_list:
                port_list.append(x)
        else:
            print ( "unknown switch attribute" )

    attr_value = sai_thrift_attribute_value_t(mac='00:77:66:55:44:33')
    attr = sai_thrift_attribute_t(id=22, value=attr_value)
    client.sai_thrift_set_switch_attribute(attr)
    switch_inited = 1


class send_1_pkt( sai_base_test.SAIThriftDataplaneTest ):
    def runTest(self):
        print
        print ( "Sending L2 packet port 1 -> port 2 [access vlan=10])" )
        switch_init(self.client)
        port1 = port_list[1]
        port2 = port_list[2]
        mac1 = '08:00:00:00:01:11'
        mac2 = '08:00:00:00:02:22'
        ip1: str = "10.0.1.1"
        ip2: str = "10.0.2.2"
        
        pkt =  Ether(src=mac1, dst=mac1)
        pkt = pkt / IP(dst=ip1) / mlass_pkt.Mlaas_p( idx = 0, grad = 1, numberOfWorker = 0 )

        # in tuple: 0 is device number, 2 is port number
        # this tuple uniquely identifies a port
        send_packet( self, ( 0, 1 ), pkt )
        verify_packets( self, pkt, device_number = 0, ports = [ 1 ] )
        # or simply
        # send_packet(self, 2, pkt)
        # verify_packets(self, pkt, ports=[1])
