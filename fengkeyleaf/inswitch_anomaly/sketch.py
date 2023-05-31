# -*- coding: utf-8 -*-
import random
from typing import (
    List, Dict, Callable
)

"""
file: .py
description:
language: python3 3.11.3
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

import fengkeyleaf.utils.my_dict as fkl_dict

IP_COUNT_STR = "count"
TLS_STR = "TLS"
# lambda to find the key-value pair with the min/max ip count.
F_COUNT: Callable = lambda p : p[ 1 ][ IP_COUNT_STR ]
# lambda to find the key-value pair with the min/max ip tls.
F_TLS: Callable = lambda p : p[ 1 ][ TLS_STR ]


class Sketch:
    TLS_THRESHOLD: int = 1000

    """
    Sketch class, Currently tracking src IP and dst IP.
    """
    # Algorithm SKETCHCLASSIFICATION( p )
    # Input. Incomming packet, p.
    # Output. List of feature values extracted from the sketch based on the packet, p.
    def __init__( self, l: int = -1 ) -> None:
        """

        @param l: Limitation to this sketch, that is, how many spots it will have.
        """
        # Initialize the following global variables:
        # c <- 0 // Global IP counter.
        self.c: int = 0
        # l <- 0 // non-positive, indicating that this sketch has no limitation.
        self.l: int = l
        # S <- Array of size of n, each element in it is a dict[ src ip, its info ].
        self.S: Dict[ str, Dict[ str, int ] ] = {}
        # D <- Array of size of n, each element in it is a dict[ dst ip, its info ].
        self.D: Dict[ str, Dict[ str, int ] ] = {}

    # Algorithm ADD( dic, ip )
    # Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
    def add( self, dic: Dict[ str, Dict[ str, int ] ], ip: str ) -> None:
        # else REPLACE( dic, ip )
        if dic.get( ip ) is None:
            self.replace( dic, ip )
            return

        # if dic contains ip:
        # then dic[ ip ][ IP_COUNT ] += 1
        dic[ ip ][ IP_COUNT_STR ] += 1
        # dic[ ip ][ IP_TLS ] = 0
        dic[ ip ][ TLS_STR ] = 0

    # Algorithm REPLACE( dic, ip )
    # Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
    def replace( self, dic: Dict[ str, Dict[ str, int ] ], ip: str ):
        # if HASEMPTY( dic )
        if self.has_empty( dic ):
            # then TREACK( dic, ip )
            Sketch.track( dic, ip )
            return

        # else r <- get a random number from 0 to 3, inclusive.
        r: int = random.randint( 0, 3 )
        # if r == 0 // Replace lowest count
        # then LOWESTCOUNT( dic, ip )
        if r == 0: Sketch.lowest_count( dic, ip );
        # else if r == 1 // Highest TLS
        # then HIGHESTTLS( dic, ip )
        elif r == 1: Sketch.highest_tls( dic, ip );
        # else if r == 2 // smallest count and tls score, calculated by count * ( 1000 - tls )
        # then SMALLFESTTLS( dic, ip )
        elif r == 2: Sketch.smallest_tls( dic, ip );
        # No replace when rand == 3

    # Algorithm HASEMPTY( dic )
    # Input. A dict, dic, to store a key-value pair, ( ip, ip's info ).
    # Output. To tell if the sketch has an empty spot or not.
    def has_empty( self, dic: Dict[ str, Dict[ str, int ] ] ) -> bool:
        return self.l <= 0 or len( dic ) < self.l

    # Algorithm TREACK( dic, ip )
    # Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
    @staticmethod
    def track( dic: Dict[ str, Dict[ str, int ] ], ip: str ) -> None:
        # assert that ip is not in dic.
        assert dic.get( ip ) is None
        # dic[ ip ][ IP_COUNT ] = 1
        # dic[ ip ][ IP_TLS ] = 0
        dic[ ip ] = {
            IP_COUNT_STR: 1,
            TLS_STR: 0
        }

    # Algorithm LOWESTCOUNT( dic, ip )
    # Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
    @staticmethod
    def lowest_count( dic: Dict[ str, Dict[ str, int ] ], ip: str ) -> None:
        # i <- Find the ip, i, so that dic[ i ][ IP_COUNT ] is the lowest in dic.
        ( k, _ ) = fkl_dict.find_min_value( dic, F_COUNT )
        # Remove the key-value pair with i as the key.
        dic.pop( k )
        # TREACK( dic, ip )
        Sketch.track( dic, ip )

    # Algorithm HIGHESTTLS( dic, ip )
    # Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
    @staticmethod
    def highest_tls( dic: Dict[ str, Dict[ str, int ] ], ip: str ) -> None:
        # i <- Find the ip, i, so that dic[ i ][ IP_TLS ] is the highest in dic.
        ( k, _ ) = fkl_dict.find_max_value( dic, F_TLS )
        # Remove the key-value pair with i as the key.
        dic.pop( k )
        # TREACK( dic, ip )
        Sketch.track( dic, ip )

    # Algorithm SMALLFESTTLS( dic, ip )
    # Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
    @staticmethod
    def smallest_tls( dic: Dict[ str, Dict[ str, int ] ], ip: str ) -> None:
        # i <- Find the ip, i, so that dic[ i ][ IP_TLS ] is the smallest in dic.
        ( k, _ ) = fkl_dict.find_min_value( dic, F_TLS )
        # Remove the key-value pair with i as the key.
        dic.pop( k )
        # TREACK( dic, ip )
        Sketch.track( dic, ip )

    def add_src( self, ip: str ) -> None:
        """
        Add a src IP.
        @param ip:
        @return:
        """
        self.add( self.S, ip )
        self.post_process()

    def add_dst( self, ip: str ) -> None:
        """
        Add a dst IP.
        @param ip:
        @return:
        """
        self.add( self.D, ip )
        self.post_process()

    def post_process( self ) -> None:
        """
        Increment TLS for all IPs.
        """
        # Increment every element in T by 1, as well as c.
        for k in self.S.keys():
            self.S[ k ][ TLS_STR ] += 1
        for k in self.D.keys():
            self.D[ k ][ TLS_STR ] += 1
        self.c += 1

        # if this sketch has limitation and c >= 1000
        if self.l > 0 and self.c >= Sketch.TLS_THRESHOLD:
            # then Reset every element in T to 0, as well as c.
            for k in self.S.keys():
                self.S[ k ][ TLS_STR ] = 0
            for k in self.D.keys():
                self.D[ k ][ TLS_STR ] = 0
                self.c = 0

    def getData( self, si: str, di: str ) -> List[ int ]:
        """
        Get one row of data.
        @param si: src ip
        @param di: dst ip
        @return: [ srcCount, srcTLS, dstCount, dstTLS ]
        """
        return [ self.S[ si ][ IP_COUNT_STR ], self.S[ si ][ TLS_STR ],
                 self.D[ di ][ IP_COUNT_STR ], self.D[ di ][ TLS_STR ] ]

    def clear( self ) -> None:
        self.c = 0
        self.l = -1
        self.D = {}
        self.S = {}