# -*- coding: utf-8 -*-

# sudo pip3 install -U pandas
# sudo pip3 install -U torch
# sudo pip3 install -U numpy
import logging
import socket
import math
import struct
import threading
from typing import Tuple, Dict

import numpy as np
# pyTorch imports
import torch
import torch.nn as nn
import torch.optim as optim
# scapy imports
import scapy.all
import scapy.packet

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging
from fengkeyleaf.my_scapy import receiver, get_if
from fengkeyleaf import annotations

__version__ = "1.0"


# Reference material: https://www.usenix.org/conference/nsdi21/presentation/sapio
@annotations.abstract_class
class Worker( threading.Thread ):
    """
    Worker side in SwitchML
    """
    SETUP_WAITING_TIME: int = 2

    EXP: int = 31
    MAX_INT: int = 2 ** EXP - 1
    MIN_INT: int = -( 2 ** EXP )

    # Format Characters
    # i - int - Integer - 4
    SEND_PAYLOAD_BYTE_PACK_FORMAT: str = "ii"
    REC_PAYLOAD_BYTE_PACK_FORMAT: str = "iii"

    SLEEP_TIME: int = 1 # 1s

    POOL_SIZE: int = 256

    # TODO: Put this class into the package, my_scapy.
    class Sender:
        """
        Sender to send pkts.
        """
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
            # https://scapy.readthedocs.io/en/latest/api/scapy.sendrecv.html#scapy.sendrecv.sendp
            scapy.all.sendp( p, iface = iface, verbose = False )

            # https://scapy.readthedocs.io/en/latest/api/scapy.packet.html#scapy.packet.Packet.show2
            return p.show2( dump = True )

    def __init__( self, lr: float, ll: int = logging.INFO ) -> None:
        super().__init__()

        # Logging
        self.l: logging.Logger = my_logging.get_logger( ll )

        # Networking communication
        # Sender setting
        self.sd: Worker.Sender = Worker.Sender( self.l )

        # TODO: How to dynamically configurate swports.
        self.swports: Dict[ int, str ] = self._config_swports()

        # Receiver setting
        self.rec: receiver.Receiver = None

        # Format: ( idx, grad( int ), number of worker )
        self.res: Tuple[ int, int, int ] = None

        # ML part
        self.X_train: torch.Tensor = None
        self.y_train: torch.Tensor = None
        self.X_valid: torch.Tensor = None
        self.y_valid: torch.Tensor = None

        self.model: nn.Sequential = None
        self.loss_fn: nn.BCELoss = None
        self.opti: optim.SGD = None
        self.lr: float = lr

        # Worker-side aggregation setting
        self.s: int = Worker.POOL_SIZE # pool size
        self.k: int = 1 # the size of the vector aggregated in each slot
        self.n: int = -1 # size of U.

        # Scaling factor
        # TODO: How to select this f?
        self.f: int = 10000 # 10 ^ 4

    @annotations.abstract_method
    def _config_swports( self ) -> Dict[ int, str ]:
        pass

    @annotations.abstract_method
    def config_receiver( self, p: int ) -> None:
        pass

    def load_data( self, f_training: str, f_valid: str = None ) -> None:
        """
        Load datasets from files.
        @param f_training: File path to the training dataset.
        @param f_valid: File path to the validation dataset.
        @return:
        """
        self.X_train, self.y_train = Worker._load_data( f_training )

        if f_valid is None or f_valid == "":
            self.X_valid = self.X_train
            self.y_valid = self.y_train
            return

        self.X_valid, self.y_valid = Worker._load_data( f_valid )

    @staticmethod
    def _load_data( f: str ) -> Tuple[ torch.Tensor, torch.Tensor ]:
        # load the dataset, split into input (X) and output (y) variables
        dataset: np.ndarray = np.loadtxt( f, delimiter = ',' )
        X: np.ndarray = dataset[ :, 0:8 ]
        y: np.ndarray = dataset[ :, 8 ]
        # print( X )
        # print( y )

        return (
            torch.tensor( X, dtype = torch.float32 ),
            torch.tensor( y, dtype = torch.float32 ).reshape( -1, 1 )
        )

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

    def training( self, ig_port: int ) -> None:
        self.l.info( "Started traininng" )

        n_epochs: int = 30
        batch_size: int = 10

        # https://pytorch.org/docs/stable/generated/torch.nn.Module.html#torch.nn.Module.parameters
        for epoch in range( n_epochs ):
            loss: torch.Tensor = None

            for i in range( 0, len( self.X_train ), batch_size ):
                self.opti.zero_grad()

                Xbatch: torch.Tensor = self.X_train[ i: i + batch_size ]
                y_pred: torch.Tensor = self.model( Xbatch )
                y_batch: torch.Tensor = self.y_train[ i: i + batch_size ]
                loss = self.loss_fn( y_pred, y_batch )
                loss.backward()

                # self.opti.step()
                self._manually_update_params( ig_port )

            self.l.info( f'Finished epoch {epoch}, latest loss {loss}' )

    # https://pytorch.org/docs/stable/generated/torch.clone.html#torch.clone
    def _manually_update_params( self, ig_port: int ) -> None:
        """
        Manually compute gradients and then update parameters.
        """
        with torch.no_grad():
            for P in self.model.parameters():
                # print( P )
                # print( P.grad )
                P.copy_(
                    self._get_average_grad(
                        P.clone(),
                        P.grad.clone(),
                        ig_port
                    )
                )

    def _get_average_grad( self, P: torch.Tensor, G: torch.Tensor, ig_port: int ) -> torch.Tensor:
        """

        @param P: List of lists of parameters.
        @param G: List of lists of gradients.
        @return:
        """
        assert len( P ) == len( G ), str( P ) + "\n" + str( G )

        # TODO: l and i would conflict in the pool index?
        for l in range( len( P ) ):
            # p - lr * grad
            # P[ l ] is a scalar.
            if len( P[ l ].size() ) == 0:
                assert len( G[ l ].size() ) == 0
                P[ l ] = P[ l ] - self.lr * self._update_gard( l, G[ l ], ig_port )
                continue

            # P[ l ] is a vector.
            assert len( P[ l ].size() ) > 0, str( P[ l ] ) + " | " + str( G[ l ] )
            assert len( P[ l ] ) == len( G[ l ] )
            for i in range( len( P[ l ] ) ):
                P[ l ][ i ] = P[ l ][ i ] - self.lr * self._update_gard( i, G[ l ][ i ], ig_port )

        return P

    @annotations.abstract_method
    def _update_gard( self, i: int, g: float, ig_port: int ) -> float:
        """
        Get a gradient value for each parameter and
        send the value to the switch to do in-switch gradient aggregation.
        @param i: Index
        @param g: Gradient value.
        @return:
        """
        pass

    @annotations.abstract_method
    def _process_rec_pkt( self, p: scapy.packet.Packet ) -> None:
        """
        Process the received pkt from the switch.
        @param p: Received pkt from the switch.
        @rtype: None
        """
        pass

    def _get_send_data( self, i: int, g: float ) -> bytes:
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
            y_pred = self.model( self.X_valid )

        accuracy = ( y_pred.round() == self.y_valid ).float().mean()
        self.l.info( f"Accuracy {accuracy}" )
