# -*- coding: utf-8 -*-

import logging

from scapy.all import IntField, ShortField, SignedIntField, BitField, Packet, bind_layers
from scapy.layers.inet import IP, Ether

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging

__version__ = "1.0"

# p = get_pkt( "08:00:00:00:01:11", "08:00:00:00:02:22", "10.0.1.1", 0, 5, 0 )
# def print_out( x ):
#     print( MlaasTofinoPacket in x )
#     x.show2()
# sniff( iface = "veth2", prn = lambda x : print_out( x ) )


l: logging.Logger = my_logging.get_logger( logging.INFO )


# https://scapy.readthedocs.io/en/latest/build_dissect.html
# https://scapy.readthedocs.io/en/latest/api/scapy.fields.html#scapy.fields.BitField
class MlaasTofinoPacket( Packet ):
    name = "Mlaas tofino packet"
    fields_desc = [
        IntField( "idx", 0 ), # Pool index field, 32 bits
        # Be careful: SignedIntField and intField.
        # https://scapy.readthedocs.io/en/latest/api/scapy.fields.html#scapy.fields.IntField
        # https://scapy.readthedocs.io/en/latest/api/scapy.fields.html#scapy.fields.SignedIntField
        SignedIntField( "v", 0 ), # Gradient value( integer ) field, 32 bits
        BitField( "sign", 0, 1 ), # Gradient value sign field, 1 bit
        BitField( "reserves", 0, 7 ), # Reserved bit field, 7 bits
        ShortField( "numberOfWorker", 0 ) # Number of woker field, 16 bits
    ]


def get_pkt(
        src_mac: str, dst_mac: str, addr: str,
        idx: int, v: int, number_of_worker: int
) -> Packet:
    pkt: Packet = Ether( src = src_mac, dst = dst_mac )
    pkt = pkt / IP( dst = addr ) / MlaasTofinoPacket(
        idx = idx, v = v, sign = True,
        reserves = 0, numberOfWorker = number_of_worker
    )
    # pkt.show2()
    return pkt


l.info( "Binding MlaasTofinoPacket" )
bind_layers( IP, MlaasTofinoPacket )

