# -*- coding: utf-8 -*-

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
import scapy.packet

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

import fengkeyleaf.utils.my_math as my_math
from fengkeyleaf.my_scapy import (
    sender,
    receiver
)

__version__ = "1.0"


class Worker:
    # Format Characters
    # i - int - Integer - 4
    SEND_PAYLOAD_BYTE_PACK_FORMAT: str = "ii"
    REC_PAYLOAD_BYTE_PACK_FORMAT: str = "iii"

    SLEEP_TIME: int = 1 # 1s

    def __init__( self, lr: float ) -> None:
        # Networking communication
        self.s: sender.Sender = sender.Sender()

        self.r: receiver.Receiver = receiver.Receiver( self.process_rec_pkt )
        self.r.get_sniffing_iface()
        self.r.start()

        self.res: Tuple = None

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

        print( self.model )

        self.loss_fn = nn.BCELoss()  # binary cross entropy
        # print( self.model.parameters() )
        # https://pytorch.org/docs/stable/generated/torch.optim.Adam.html#torch.optim.Adam
        # self.opti = optim.Adam( self.model.parameters(), lr = 0.001 )
        # https://pytorch.org/docs/stable/generated/torch.optim.SGD.html#torch.optim.SGD
        self.opti = optim.SGD( self.model.parameters(), self.lr )

    def training( self ) -> None:
        n_epochs: int = 100
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

            print( f'Finished epoch {epoch}, latest loss {loss}' )

    # https://pytorch.org/docs/stable/generated/torch.clone.html#torch.clone
    def manually_update_params( self ) -> None:
        with torch.no_grad():
            for P in self.model.parameters():
                P.copy_( self.get_average_grad( P.clone() ) )

    def get_average_grad( self, P: torch.Tensor ) -> torch.Tensor:
        assert len( P ) == len( P.grad )

        for i in range( len( P ) ):
            # TODO: Dst ip and dst interface.
            self.s.send( "", "", self.get_send_data( i, P.grad[ i ] ) )

            # TODO: synchronize worker and switch to get a gradient update pkt.
            while self.res is None:
                sleep( Worker.SLEEP_TIME )

            assert self.res is not None
            assert my_math.assert_overflow( self.res[ 1 ], self.res[ 1 ] / self.f )
            avg_grad: float = self.res[ 1 ] / (self.f * self.res[ 2 ])
            P[ i ] = P[ i ] - self.lr * avg_grad

        return P

    def process_rec_pkt( self, p: scapy.packet.Packet ) -> None:
        """
        Process the received pkt from the switch.
        @param p: Received pkt from the switch.
        @rtype: None
        """
        assert self.res is None
        self.res = struct.unpack( Worker.REC_PAYLOAD_BYTE_PACK_FORMAT, p[ scapy.packet.Raw ].load )

    def get_send_data( self, i: int, g: float ) -> bytes:
        """

        @param i: Index for the gradient, g.
        @param g: Gradient value in floating point number
        """
        assert my_math.assert_overflow( g, g * self.f )

        grad: int = math.ceil( g * self.f )
        b: bytes = struct.pack( Worker.SEND_PAYLOAD_BYTE_PACK_FORMAT, i, grad )
        return b

    def evaluate( self ) -> None:
        # compute accuracy (no_grad is optional)
        with torch.no_grad():
            y_pred = self.model( self.X )

        accuracy = ( y_pred.round() == self.y ).float().mean()
        print( f"Accuracy {accuracy}" )
