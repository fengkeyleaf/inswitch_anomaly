# -*- coding: utf-8 -*-

import logging
import math
from time import sleep
from typing import Dict

# scapy imports
import scapy.packet
# pyTorch imports
from scapy.layers.inet import IP, Ether

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.my_scapy import receiver
from fengkeyleaf.mlaas_preli import worker, mlaas_pkt
from fengkeyleaf import annotations

__version__ = "1.0"


class Worker( worker.Worker ):
    def __init__(
            self, lr: float,
            name: str = "Default worker bmv2 name", ll: int = logging.INFO
    ) -> None:
        super().__init__( lr, name, ll )
        mlaas_pkt.binding()

    """
    Worker side in SwitchML
    """
    @annotations.override
    def _config_swports( self ) -> Dict[ int, str ]:
        return {
            # port : iface
            0: "eth0"
        }

    @annotations.override
    def config_receiver( self, p: int ) -> None:
        self.rec = receiver.Receiver( self._process_rec_pkt )
        self.rec.get_sniffing_iface()
        self.rec.start()

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

        ( pos, neg, sign ) = mlaas_pkt.convert_to_pkt( math.ceil( g * self.f ) )
        # TODO: Dst ip and dst interface.
        pkt_str: str = self.sd.send(
            "10.0.1.1", self.swports[ ig_port ],
            mlaas_pkt.get_mlaas_pkt(
                "08:00:00:00:01:11", "08:00:00:00:02:22", "10.0.1.1", 64,
                i, pos, neg, sign, 0
            )
        )
        self.l.debug( "Sent:" + pkt_str )

        # TODO: synchronize worker and switch to get a gradient update pkt.
        while self.res is None:
            sleep( Worker.SLEEP_TIME )

        assert self.res is not None
        self.l.debug( f"idx={self.res[ 0 ]}, grad={self.res[ 1 ]}, # of worker={self.res[ 2 ]}" )
        avg_grad: float = self.res[ 1 ] / (self.f * self.res[ 2 ])

        self.res = None  # Reset container to assert.
        return avg_grad

    # TODO: pkt loss
    @annotations.override
    def _process_rec_pkt( self, p: scapy.packet.Packet ) -> None:
        """
        Process the received pkt from the switch.
        @param p: Received pkt from the switch.
        @rtype: None
        """
        if mlaas_pkt.Mlaas_p not in p:
            return

        self.l.debug( "Rec:" + p.show2( dump = True ) )
        assert self.res is None
        self.res = ( p.idx, p.gradPos - p.gradNeg, p.numberOfWorker )

        # 6: repeat
        # 7: receive p(idx, off, vector)
        # 8: A[p.off : p.off +k] <- p.vector
        # 9: p.off <- p.off + k · s
        # p.off = p.off + self.k * self.s
        # assert self.n >= 0
        # 10: if p.off < size(U) then
        # if p.off < self.n:
        # 11: p.vector U[p.off : p.off + k]
        # 12: send p
        # 13: until A is incomplete

    @staticmethod
    def print_info_rec( p: scapy.packet.Packet ) -> None:
        print( "process_rec_pkt" )
        p.show2()
        print( mlaas_pkt.Mlaas_p in p )
        print( IP in p )
        print( Ether in p )
        # exit( 1 )


if __name__ == '__main__':
    lr: float = 0.001
    w: Worker = Worker( lr )
    w.config_receiver( -1 )
    w.build_model()
    w.load_data( "./fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data.csv" )
    w.training( 0 )
    w.evaluate()
