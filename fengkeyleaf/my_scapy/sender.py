# -*- coding: utf-8 -*-

import random
import logging
import socket
# scapy imports
import scapy.all
from scapy.layers.inet import (
    IP,
    Ether,
    TCP
)
import scapy.packet

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging
from fengkeyleaf.my_scapy import get_if

__version__ = "1.0"


class Sender:
    def __int__( self, ll: int = logging.INFO ):
        self.l: logging.Logger = my_logging.get_logger( ll )

    # p: str | bytes are both OK using scapy.packet.Raw( load = p ) to generate a pkt.
    def send( self, ip: str, target_iface: str, p: str | bytes ) -> str:
        """
        Send a pkt to the ip with target_interface and port.
        @param ip: Dst ip to which the pkt will be sent
        @type ip: str
        @param target_iface: Target Interface to which the pkt will be sent
        @type target_iface: str
        @param p: payload
        @type p: str
        @return: A hierarchical view of an assembled version of the packet
        @rtype: str
        """
        addr: str = socket.gethostbyname( ip )
        iface: str = get_if( target_iface )

        pkt: scapy.packet.Packet = Ether( src = scapy.all.get_if_hwaddr( iface ), dst = 'ff:ff:ff:ff:ff:ff' )
        pkt = pkt / IP( dst = addr ) / TCP(
            dport = 1234, sport = random.randint( 49152, 65535 )
        ) / scapy.packet.Raw( load = p )

        self.l.info( "Sending on interface %s to %s" % ( iface, str( addr ) ) )
        scapy.all.sendp( pkt, iface = iface, verbose = False )

        # https://scapy.readthedocs.io/en/latest/api/scapy.packet.html#scapy.packet.Packet.show2
        return pkt.show2( dump = True )

