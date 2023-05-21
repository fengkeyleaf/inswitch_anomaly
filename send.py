#!/usr/bin/env python3
import random
import socket
import sys
from argparse import (
    ArgumentParser
)
from typing import Dict
import json

"""
file:
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp
from imports import topo


# Refernce material:
# https://github.com/p4lang/tutorials


def get_if():
    ifs = get_if_list()
    iface = None  # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break;
    if not iface:
        print( "Cannot find eth0 interface" )
        exit( 1 )
    return iface


def main():
    # if len(sys.argv)<3:
    #     print('pass 2 arguments: <destination> "<message>"')
    #     exit(1)

    parser: ArgumentParser = ArgumentParser()
    parser.add_argument( "-d", "--dst", type = str, help = "Path to host json", required = False, default = "" )
    parser.add_argument( "-m", "--msg", type = str, help = "Path to host json", required = False, default = "" )
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    parser.add_argument( "-hj", "--host_json", type = str, help = "Path to host json", required = False, default = "" )

    args = parser.parse_args()

    # addr = socket.gethostbyname( args.dst )
    iface = get_if()

    with open( args.host_json, "r" ) as f:
        P: Dict = json.load( f )[ topo.PKT_STR ]
        for k in P:
            addr: str = socket.gethostbyname( P[ k ][ topo.DST_IP_STR ] )
            print( "sending on interface %s to %s" % (iface, str( addr )) )
            pkt = Ether( src = get_if_hwaddr( iface ), dst = 'ff:ff:ff:ff:ff:ff' )
            pkt = pkt / IP( dst = addr ) / TCP( dport = 1234, sport = random.randint( 49152, 65535 ) ) / k
            pkt.show2()
            sendp( pkt, iface = iface, verbose = False )


if __name__ == '__main__':
    main()
