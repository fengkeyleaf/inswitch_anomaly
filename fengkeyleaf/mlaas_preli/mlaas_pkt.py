# -*- coding: utf-8 -*-

from typing import Tuple

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
class Mlaas_p( Packet ):
    name = "Mlaas packet"
    fields_desc = [
        IntField( "idx", 0 ),
        # Be careful: SignedIntField and intField.
        IntField( "gradPos", 0 ),
        IntField( "gradNeg", 0 ),
        BitField( "sign", 0, 1 ),
        BitField( "reserves", 0, 7 ),
        ShortField( "numberOfWorker", 0 )
    ]


def convert_to_pkt( g: int ) -> Tuple[ int, int, bool ]:
    pos: int = 0
    neg: int = 0
    sign: bool = False # Positive

    if g < 0:
        sign = True
        neg = abs( g )
    else:
        pos = g

    return ( pos, neg, sign )


def get_mlaas_pkt(
        src_mac: str, dst_mac: str, addr, ttl: int,
        idx: int, gradPos: int, gradNeg: int, sign: bool, number_of_worker: int
) -> Packet:
    pkt = Ether( src = src_mac, dst = dst_mac )
    pkt = pkt / IP( dst = addr, ttl = ttl ) / Mlaas_p(
        idx = idx, gradPos = gradPos, gradNeg = gradNeg,
        sign = sign, reserves = 0, numberOfWorker = number_of_worker
    )
    # pkt.show2()
    return pkt


bind_layers( IP, Mlaas_p )

