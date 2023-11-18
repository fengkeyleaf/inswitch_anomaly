# -*- coding: utf-8 -*-

from scapy.all import IntField, ShortField, BitField, Packet, bind_layers
from scapy.layers.inet import IP, Ether

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""


# https://scapy.readthedocs.io/en/latest/build_dissect.html
# https://scapy.readthedocs.io/en/latest/api/scapy.fields.html#scapy.fields.BitField
class MlaasTofinoPacket( Packet ):
    name = "Mlaas tofino packet"
    fields_desc = [
        IntField( "idx", 0 ),
        # Be careful: SignedIntField and intField.
        IntField( "v", 0 ),
        BitField( "sign", 0, 1 ),
        BitField( "reserves", 0, 7 ),
        ShortField( "numberOfWorker", 0 )
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


bind_layers( IP, MlaasTofinoPacket )

