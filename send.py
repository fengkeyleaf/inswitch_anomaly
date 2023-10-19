#!/usr/bin/env python3
import random
import socket
import os
from argparse import (
    ArgumentParser
)
from typing import Dict
import json
from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp

"""
file:
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf import topo, my_writer, my_files

# TODO: Merge multiple send.py into one file
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


# python3 ./send.py -hjs ./pod-topo/hosts/
def send_pkts_hosts( fp: str, iface: str ) -> None:
    """
    Send pkts from different host json file on the same host.
    """
    for s, d, F in os.walk( fp ):
        for f in F:
            assert my_writer.get_extension( f ).lower() == my_files.JSON_EXTENSION, f

            with open( os.path.join( s, f ), "r" ) as f_json:
                # Host info
                H: Dict = json.load( f_json )
                src_addr: str = H[ topo.IP_STR ]
                print( "Start sending pkts on srcIP=%s, h=%s" % ( src_addr, f ) )
                # Pkt info
                P: Dict  = H[ topo.PKT_STR ]
                for k in P:
                    dst_addr: str = P[ k ][ topo.DST_IP_STR ]
                    pkt = Ether( src = get_if_hwaddr( iface ), dst = 'ff:ff:ff:ff:ff:ff' )
                    pkt = pkt / IP( src = src_addr, dst = dst_addr )
                    pkt = pkt / TCP( dport = 1234, sport = random.randint( 49152, 65535 ) ) / k
                    # pkt.show2()
                    sendp( pkt, iface = iface, verbose = False )
                print( "Done with sending pkts on %s" % ( src_addr ) )


    print( "Done with sending all pkts" )


def main():
    # if len(sys.argv)<3:
    #     print('pass 2 arguments: <destination> "<message>"')
    #     exit(1)

    parser: ArgumentParser = ArgumentParser()
    parser.add_argument( "-d", "--dst", type = str, help = "Path to host json", required = False, default = "" )
    parser.add_argument( "-m", "--msg", type = str, help = "Path to host json", required = False, default = "" )
    # https://stackoverflow.com/questions/18839957/argparseargumenterror-argument-h-help-conflicting-option-strings-h
    parser.add_argument( "-hj", "--host_json", type = str, help = "Path to host json", required = False, default = None )
    parser.add_argument( "-hjs", "--host_jsons", type = str, help = "Directory path to host jsons", required = False, default = None )

    args = parser.parse_args()

    # addr = socket.gethostbyname( args.dst )
    iface: str = get_if()

    if args.host_jsons is not None:
        send_pkts_hosts( args.host_jsons, iface )
        return

    # TODO: Send pkts with multiple hosts in parallel. 
    # send_pkts_host()


if __name__ == '__main__':
    main()
