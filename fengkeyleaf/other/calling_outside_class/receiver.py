# -*- coding: utf-8 -*-

from typing import Callable
import threading


"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"


class Receiver( threading.Thread ):
    def __init__(
            self, prn: Callable = None
    ) -> None:
        super().__init__()

        self.prn: Callable = prn

    def receive( self, prn: Callable ):
        prn( "String passed from the Receiver!" )

    def run( self ) -> None:
        self.prn("String passed from the Receiver(Thread)!" )
