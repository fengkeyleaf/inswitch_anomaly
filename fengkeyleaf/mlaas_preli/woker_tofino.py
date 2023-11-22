# -*- coding: utf-8 -*-

import logging
import math
from time import sleep
from typing import Dict

# scapy imports
import scapy.packet
import scapy.all

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.my_scapy import receiver
from fengkeyleaf.mlaas_preli import worker, mlaas_pkt_tofino
from fengkeyleaf import annotations

__version__ = "1.0"


class Worker( worker.Worker ):

    def __init__( self, lr: float, ll: int = logging.INFO ) -> None:
        super().__init__( lr, ll )
        mlaas_pkt_tofino.binding()

    @annotations.override
    def config_receiver( self, p: int ) -> None:
        self.rec = receiver.Receiver( self._process_rec_pkt )
        self.rec.iface = self.swports[ p ]
        self.rec.start()

    @annotations.override
    def _config_swports( self ) -> Dict[ int, str ]:
        # Adding interface veth0 as port 0
        # Adding interface veth2 as port 1
        # Adding interface veth4 as port 2
        # Adding interface veth6 as port 3
        # Adding interface veth8 as port 4
        # Adding interface veth10 as port 5
        # Adding interface veth12 as port 6
        # Adding interface veth14 as port 7
        # Adding interface veth16 as port 8
        # Adding interface veth18 as port 9
        # Adding interface veth20 as port 10
        # Adding interface veth22 as port 11
        # Adding interface veth24 as port 12
        # Adding interface veth26 as port 13
        # Adding interface veth28 as port 14
        # Adding interface veth30 as port 15
        # Adding interface veth32 as port 16
        # Adding interface veth250 as port 64
        return {
            # port : iface
            0: "veth0",
            1: "veth2",
            2: "veth4"
        }

    @annotations.override
    def _update_gard( self, i: int, g: float, ig_port: int ) -> float:
        """
        Get a gradient value for each parameter and
        send the value to the switch to do in-switch gradient aggregation.
        @param i: Index
        @param g: Gradient value.
        @return:
        """
        assert i < self.s
        assert g * self.f <= Worker.MAX_INT

        # TODO: Dst ip and dst interface.
        pkt_str: str = self.sd.send(
            "10.0.1.1", self.swports[ ig_port ],
            mlaas_pkt_tofino.get_pkt(
                "08:00:00:00:01:11", "08:00:00:00:02:22", "10.0.1.1",
                i, math.ceil( g * self.f ), 0
            )
        )
        self.l.debug( "Sent:" + pkt_str )

        # TODO: synchronize worker and switch to get a gradient update pkt.
        while self.res is None:
            sleep( Worker.SLEEP_TIME )

        assert self.res is not None
        self.l.debug( f"idx={self.res[ 0 ]}, grad={self.res[ 1 ]}, # of worker={self.res[ 2 ]}" )
        avg_grad: float = self.res[ 1 ] / ( self.f * self.res[ 2 ] )

        self.res = None  # Reset container to assert.
        return avg_grad

    @annotations.override
    def _process_rec_pkt( self, p: scapy.packet.Packet ) -> None:
        """
        Process the received pkt from the switch.
        @param p: Received pkt from the switch.
        @rtype: None
        """
        # multicast pkts will be considered as incoming pkts in tofino,
        # pkts with numberOfWorker > 0 are outcoming ones.
        if mlaas_pkt_tofino.MlaasTofinoPacket not in p or p.numberOfWorker <= 0:
            return

        self.l.debug( "Rec:" + p.show2( dump = True ) )
        assert self.res is None
        self.res = ( p.idx, p.v, p.numberOfWorker )
