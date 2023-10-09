# -*- coding: utf-8 -*-

# sudo pip3 install -U pandas
# sudo pip3 install -U torch
# sudo pip3 install -U numpy
import logging
import socket
import math
import struct
from time import sleep
from typing import Tuple
import numpy as np
# pyTorch imports
import torch
import torch.nn as nn
import torch.optim as optim
# scapy imports
import scapy.all
import scapy.packet
from scapy.layers.inet import IP, Ether

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging
from fengkeyleaf.my_scapy import (
    receiver,
    get_if
)
from fengkeyleaf.mlaas_preli import mlaas_pkt

__version__ = "1.0"


class Worker:
    EXP: int = 31
    MAX_INT: int = 2 ** EXP - 1
    MIN_INT: int = -( 2 ** EXP )

    # Format Characters
    # i - int - Integer - 4
    SEND_PAYLOAD_BYTE_PACK_FORMAT: str = "ii"
    REC_PAYLOAD_BYTE_PACK_FORMAT: str = "iii"

    SLEEP_TIME: int = 1 # 1s

    POOL_SIZE: int = 32

    # TODO: Put this class into the package, my_scapy.
    class _Sender:
        def __init__( self, l: logging.Logger ):
            self.l: logging.Logger = l

        # p: str | bytes are both OK using scapy.packet.Raw( load = p ) to generate a pkt.
        def send( self, ip: str, target_iface: str, p: scapy.packet.Packet ) -> str:
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

            self.l.debug( "Sending on interface %s to %s" % ( iface, str( addr ) ) )
            scapy.all.sendp( p, iface = iface, verbose = False )

            # https://scapy.readthedocs.io/en/latest/api/scapy.packet.html#scapy.packet.Packet.show2
            return p.show2( dump = True )

    def __init__( self, lr: float, ll: int = logging.INFO ) -> None:
        self.l: logging.Logger = my_logging.get_logger( ll )

        # Networking communication
        self.s: Worker._Sender = Worker._Sender( self.l )

        self.r: receiver.Receiver = receiver.Receiver( self.process_rec_pkt )
        self.r.get_sniffing_iface()
        self.r.start()

        # Format: ( idx, grad( int ), number of worker )
        self.res: Tuple[ int, int, int ] = None

        # ML part
        self.X: torch.Tensor = None
        self.y: torch.Tensor = None
        self.model: nn.Sequential = None
        self.loss_fn: nn.BCELoss = None
        self.opti: optim.SGD = None
        self.lr: float = lr

        # Scaling factor
        # TODO: How to select this f?
        self.f: int = 10000 # 10 ^ 4

    def load_data( self, f: str ) -> None:
        # load the dataset, split into input (X) and output (y) variables
        dataset: np.ndarray = np.loadtxt( f, delimiter = ',' )
        X: np.ndarray = dataset[ :, 0:8 ]
        y: np.ndarray = dataset[ :, 8 ]
        # print( X )
        # print( y )

        self.X = torch.tensor( X, dtype = torch.float32 )
        self.y = torch.tensor( y, dtype = torch.float32 ).reshape( -1, 1 )

    def build_model( self ) -> None:
        self.model = nn.Sequential(
            nn.Linear( 8, 12 ),
            nn.ReLU(),
            nn.Linear( 12, 8 ),
            nn.ReLU(),
            nn.Linear( 8, 1 ),
            nn.Sigmoid()
        )

        self.l.info( self.model )

        self.loss_fn = nn.BCELoss()  # binary cross entropy
        # print( self.model.parameters() )
        # https://pytorch.org/docs/stable/generated/torch.optim.Adam.html#torch.optim.Adam
        # self.opti = optim.Adam( self.model.parameters(), lr = 0.001 )
        # https://pytorch.org/docs/stable/generated/torch.optim.SGD.html#torch.optim.SGD
        self.opti = optim.SGD( self.model.parameters(), self.lr )

    def training( self ) -> None:
        n_epochs: int = 30
        batch_size: int = 10

        # https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.parameters
        for epoch in range( n_epochs ):
            loss: torch.Tensor = None

            for i in range( 0, len( self.X ), batch_size ):
                self.opti.zero_grad()

                Xbatch: torch.Tensor = self.X[ i : i + batch_size ]
                y_pred: torch.Tensor = self.model( Xbatch )
                y_batch: torch.Tensor = self.y[ i : i + batch_size ]
                loss = self.loss_fn( y_pred, y_batch )
                loss.backward()

                # self.opti.step()
                self.manually_update_params()

            self.l.info( f'Finished epoch {epoch}, latest loss {loss}' )

    # https://pytorch.org/docs/stable/generated/torch.clone.html#torch.clone
    def manually_update_params( self ) -> None:
        with torch.no_grad():
            for P in self.model.parameters():
                # print( P )
                # print( P.grad )
                P.copy_( self.get_average_grad( P.clone(), P.grad.clone() ) )

    def update_gard( self, i: int, g: float ) -> float:
        assert i < Worker.POOL_SIZE
        assert g * self.f <= Worker.MAX_INT

        ( pos, neg, sign ) = mlaas_pkt.convert_to_pkt( math.ceil( g * self.f ) )
        # TODO: Dst ip and dst interface.
        pkt_str: str = self.s.send(
            "10.0.1.1", "eth0",
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

    def get_average_grad( self, P: torch.Tensor, G: torch.Tensor ) -> torch.Tensor:
        # print( P )
        # print( G )
        assert len( P ) == len( G )

        # TODO: l and i would conflict in the pool index?
        for l in range( len( P ) ):
            # p - lr * grad
            # P[ l ] is a scalar.
            if len( P[ l ].size() ) == 0:
                assert len( G[ l ].size() ) == 0
                P[ l ] = P[ l ] - self.lr * self.update_gard( l, G[ l ] )
                continue

            # P[ l ] is a vector.
            assert len( P[ l ].size() ) > 0, str( P[ l ] ) + " | " + str( G[ l ] )
            assert len( P[ l ] ) == len( G[ l ] )
            for i in range( len( P[ l ] ) ):
                P[ l ][ i ] = P[ l ][ i ] - self.lr * self.update_gard( i, G[ l ][ i ] )

        return P

    # TODO: pkt loss
    def process_rec_pkt( self, p: scapy.packet.Packet ) -> None:
        """
        Process the received pkt from the switch.
        @param p: Received pkt from the switch.
        @rtype: None
        """
        # print( "process_rec_pkt" )
        # p.show2()
        # print( mlaas_pkt.Mlaas_p in p )
        # print( IP in p )
        # print( Ether in p )
        # exit( 1 )
        if mlaas_pkt.Mlaas_p in p:
            self.l.debug( "Rec:" + p.show2( dump = True ) )
            assert self.res is None
            self.res = ( p.idx, p.gradPos - p.gradNeg, p.numberOfWorker )

    def get_send_data( self, i: int, g: float ) -> bytes:
        """

        @param i: Index for the gradient, g.
        @param g: Gradient value in floating point number
        """
        assert g * self.f <= Worker.MAX_INT

        grad: int = math.ceil( g * self.f )
        b: bytes = struct.pack( Worker.SEND_PAYLOAD_BYTE_PACK_FORMAT, i, grad )
        return b

    def evaluate( self ) -> None:
        # compute accuracy (no_grad is optional)
        with torch.no_grad():
            y_pred = self.model( self.X )

        accuracy = ( y_pred.round() == self.y ).float().mean()
        self.l.info( f"Accuracy {accuracy}" )


if __name__ == '__main__':
    lr: float = 0.001
    w: Worker = Worker( lr )
    w.build_model()
    w.load_data( "./fengkeyleaf/mlaas_preli/test_data/pima-indians-diabetes.data.csv" )
    w.training()
    w.evaluate()
