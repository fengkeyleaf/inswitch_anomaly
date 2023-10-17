# -*- coding: utf-8 -*-

import os
import sys
import threading
import logging
from typing import Callable
import scapy.all

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging

__version__ = "1.0"


class Receiver( threading.Thread ):
    def __init__(
            self, prn: Callable = None, ll: int = logging.INFO
    ) -> None:
        super().__init__()

        self.iface: str = None
        self.prn: Callable = prn

        self.l: logging.Logger = my_logging.get_logger( ll )

    # TODO: Provide a parameter iface to be sniffed on.
    def get_sniffing_iface( self ) -> None:
        ifaces = [ i for i in os.listdir( '/sys/class/net/' ) if 'eth' in i ]
        self.iface = ifaces[ 0 ]
        sys.stdout.flush()
        self.l.info( "sniffing on %s" % self.iface )

    # https://stackoverflow.com/questions/24664893/python-scapy-sniff-only-incoming-packets/75405277#75405277
    def run( self ) -> None:
        """
        Only sniff incoming pkts.
        """
        scapy.all.sniff( iface = self.iface, filter = "inbound", prn = lambda x: self.prn( x ) )
