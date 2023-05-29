# -*- coding: utf-8 -*-

from typing import (
    List, Dict
)

"""
file: .py
description:
language: python3 3.11.3
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""


IP_COUNT_STR = "count"
TLS_STR = "TLS"


class Sketch:
    """
    Sketch class. Currently tracking src IP and dst IP.
    """
    def __init__( self ) -> None:
        self.S: Dict[ str, Dict[ str, int ] ] = {}
        self.D: Dict[ str, Dict[ str, int ] ] = {}

    def add_src( self, ip: str ) -> None:
        """
        Add a src IP.
        @param ip:
        @return:
        """
        # Otherwise set its count = 1 and TLS = 0.
        if self.S.get( ip ) is None:
            self.S[ ip ] = {
                IP_COUNT_STR: 1,
                TLS_STR: 0
            }
            return

        # If they are in s, increment its count by 1.
        self.S[ ip ][ IP_COUNT_STR ] += 1

    def add_dst( self, ip: str ) -> None:
        """
        Add a dst IP.
        @param ip:
        @return:
        """
        if self.D.get( ip ) is None:
            self.D[ ip ] = {
                IP_COUNT_STR: 1,
                TLS_STR: 0
            }
            return

        self.D[ ip ][ IP_COUNT_STR ] += 1

    def incrementTLS( self ) -> None:
        """
        Increment TLS for all IPs.
        """
        for k in self.S.keys():
            self.S[ k ][ TLS_STR ] += 1
        for k in self.D.keys():
            self.D[ k ][ TLS_STR ] += 1

    def getData( self, si: str, di: str ) -> List[ int ]:
        """
        Get one row of data.
        @param si:
        @param di:
        @return: [ srcCount, srcTLS, dstCount, dstTLS ]
        """
        return [ self.S[ si ][ IP_COUNT_STR ], self.S[ si ][ TLS_STR ],
                 self.D[ di ][ IP_COUNT_STR ], self.D[ di ][ TLS_STR ] ]