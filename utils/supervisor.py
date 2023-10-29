# -*- coding: utf-8 -*-

from typing import Dict, List
import threading
from time import sleep

from mininet.net import Mininet
from mininet.net import Host

"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""


class Supervisor:
    SLEEP_TIME = 10 # sec
    LISTENING_HOST = "h1"

    def __init__( self, net: Mininet, hosts: Dict ) -> None:
        self.__net: Mininet = net
        self.__hosts: Dict = hosts
        self.__S: List[ bool ] = []

    # https://superfastpython.com/extend-thread-class/
    class __Sender( threading.Thread ):
        # https://stackoverflow.com/a/7445805
        def __init__( self, hn: str, h: Host, c: str, id: int, S: List[ bool ] ) -> None:
            """

            @param hn: Host name containing the src IP.
            @param h: Host to actually send pkts.
            @param c: Command line to send pkts.
            @param id: Host mapping id, associated with S.
            @param S: List of boolean values to tell
                      whether it's done to send pkts on a host with the mapping id.
            """
            super().__init__()
            self.hn: str = hn
            self.h: Host = h
            self.c: str = c
            assert id > -1
            self.id: int = id
            assert id + 1 == len( S )
            self.S = S

        def run( self ) -> None:
            self.h.cmdPrint( self.c )

            print( "Done with sending pkts on %s" % ( self.hn ) )
            self.S[ self.id ] = True

    def __listening( self, h:str ) -> None:
        print( "Listening on %s" % ( self.__net.get( h ) ) )
        # print( self.net.get( h ).cmd( "./receive.py" ) )
        self.__net.get( h ).cmd( "./receive.py -c %s" % 0 )

    def __get_sum_pkts( self ) -> int:
        c: int = 0
        for hn in self.__hosts.keys():
            c = c + len( self.__hosts[ hn ][ "pkts" ] )

        return c

    def __continues( self ) -> bool:
        for b in self.__S:
            if not b:
                return True

        return False

    def _start_sniffing( self ) -> None:
        # http://mininet.org/api/classmininet_1_1node_1_1Node.html#a6e1338af3c4a0348963a257ac548153b
        # https://www.geeksforgeeks.org/multithreading-python-set-1/
        # https://docs.python.org/3.8/library/threading.html
        threading.Thread(
            target = self.__listening,
            args = ( Supervisor.LISTENING_HOST, )
        ).start()

        sleep( 2 )

    def sends( self ) -> None:
        self._start_sniffing()

        print( "Sending pkts in parallel" )
        for hn in self.__hosts.keys():
            if hn == Supervisor.LISTENING_HOST:
                continue

            self.__S.append( False )
            print( "Start sending pkts on %s" % ( hn ) )
            self.__Sender(
                hn, self.__net.get( hn ), "./send.py -hj ./pod-topo/%s.json" % ( hn ),
                len( self.__S ) - 1, self.__S
            ).start()

        while self.__continues():
            sleep( Supervisor.SLEEP_TIME )

        print( "Done with sending %d pkts" % self.__get_sum_pkts() )
        print( "Killing the listening host, %s" % ( Supervisor.LISTENING_HOST ) )
        # https://github.com/mininet/mininet/blob/master/mininet/node.py#L328
        self.__net.get( Supervisor.LISTENING_HOST ).sendInt()

    SENSING_HOST_NAME: str = "h2"

    def send( self ) -> None:
        self._start_sniffing()

        print( "Sending pkts on host %s" % (Supervisor.SENSING_HOST_NAME) )
        self.__S.append( False )
        self.__Sender(
            Supervisor.SENSING_HOST_NAME, self.__net.get( Supervisor.SENSING_HOST_NAME ),
            "./send.py -hjs ./pod-topo/hosts/",
            len( self.__S ) - 1, self.__S
        ).start()

        while self.__continues():
            sleep( Supervisor.SLEEP_TIME )

        print( "Killing the listening host, %s" % ( Supervisor.LISTENING_HOST ) )
        # https://github.com/mininet/mininet/blob/master/mininet/node.py#L328
        self.__net.get( Supervisor.LISTENING_HOST ).sendInt()