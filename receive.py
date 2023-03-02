#!/usr/bin/env python3
import os
import sys
import json
from typing import Dict
from argparse import (
    ArgumentParser
)
from datetime import (
    datetime
)

"""
file:
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from scapy.all import (
    TCP,
    Raw,
    FieldLenField,
    FieldListField,
    IntField,
    IPOption,
    ShortField,
    get_if_list,
    sniff
)
from scapy.layers.inet import _IPOption_HDR

# Refernce material: 
# https://github.com/p4lang/tutorials

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swids",
                                  adjust=lambda pkt,l:l+4),
                    ShortField("count", 0),
                    FieldListField("swids",
                                   [],
                                   IntField("", 0),
                                   length_from=lambda pkt:pkt.count*4) ]
def handle_pkt( pkt, dic:Dict ):
    if TCP in pkt and pkt[TCP].dport == 1234:
        print("got a packet")
        # https://scapy.readthedocs.io/en/latest/api/scapy.packet.html
        pkt.show2()
        # https://stackoverflow.com/questions/65370305/extracting-tcp-data-with-scapy
        # https://scapy.readthedocs.io/en/latest/api/scapy.packet.html#scapy.packet.Raw
        # print( "payload: %s" % pkt[ Raw ].load )
        # https://www.geeksforgeeks.org/how-to-convert-bytes-to-string-in-python/
        dic[ pkt[ Raw ].load.decode() ] = ""
    #    hexdump(pkt)
        sys.stdout.flush()

#  "01/03/2023 03:09:23"
def main():
    parser:ArgumentParser = ArgumentParser()
    parser.add_argument( "-c", "--count", type = int, help="Number of pkts to receive", required = False, default = 0 )

    ifaces = [i for i in os.listdir('/sys/class/net/') if 'eth' in i]
    iface = ifaces[0]
    print("sniffing on %s" % iface)
    sys.stdout.flush()

    dic:Dict = { "now":  datetime.now().strftime( "%d/%m/%Y %H:%M:%S" ) }
    # https://scapy.readthedocs.io/en/latest/api/scapy.sendrecv.html#scapy.sendrecv.sniff
    sniff( iface = iface,
        #   count = parser.parse_args().count,
        #   timeout = 10,
          prn = lambda x: handle_pkt( x, dic ) )

    print( "Finish sniffing, write result to the file" )
    with open( "./output.json", "w" ) as f:
        f.write( json.dumps( dic, indent = 4 ) )

if __name__ == '__main__':
    main()
