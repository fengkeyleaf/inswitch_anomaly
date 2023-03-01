import json
from typing import Dict, List

"""
file: topo.py
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
"""

from . import csvparaser

IP_STR = "ip"
MAC_STR = "mac"
COM_STR = "commands"
HOST_STR = "hosts"
SWITCH_STR = "switches"
LINK_STR = "links"
NAME_STR = "name"
PKT_STR = "pkts"

# https://www.geeksforgeeks.org/python-classes-and-objects/
# https://www.geeksforgeeks.org/g-fact-34-class-or-static-variables-in-python/
# https://www.geeksforgeeks.org/access-modifiers-in-python-public-private-and-protected/
class CSVParaser:
    # https://pythonexamples.org/python-write-json-to-file/
    def __generate_topo_json( self, H:Dict, S:Dict, L:List ) -> str:
        """
        :param I: List of hosts and their configurations.
        :param S: List of swtiches and their configurations.
        :param L: List of links and their configurations.
        :return: 
        """
        return json.dumps( {
            "hosts": H,
            "switches": S,
            "links": L
        }, indent = 4 )
    
    def __write_to_file( self, topo, fp ):
        with open( fp, "w+" ) as f:
            f.write( topo )

    def __add_pkt( self, h:Dict, da:str, dm:str, id:str ):
        assert h[ PKT_STR ].get( id ) is None

        h[ PKT_STR ][ id ] = {
            "dstAddr": da,
            "dstMac": dm
        }

    def __add_host( self, H:Dict[ str, Dict ], L:List, id:str, a:str, m:str ) -> Dict:
        hn:str = "h" + str( id ) # host name
        # Initi host
        h:Dict = {
            NAME_STR: hn,
            IP_STR: a,
            MAC_STR: m,
            COM_STR: [ "route add default gw " + a + " dev eth0" ],
            PKT_STR: {}
        }

        # Add link
        L.append( [ hn, "s1-p" + str( id) ] )

        H[ a ] = h
        return h

    def __get_host_json( 
        self, n: str, i: str, m: str, c:List[ str ]
    ) -> Dict:
        return ( n, {
            IP_STR: i,
            MAC_STR: m,
            COM_STR: c
        } )

    def __add_host_pkt( 
        self, H:Dict, L:List, idh:str, sa:str, da:str, sm:str, dm:str, idp:str 
    ) -> None:
        self.__add_pkt( self.__add_host( H, L, idh, sa, sm ), da, dm, idp )
    
    def __convert( self, H:Dict ) -> Dict:
        P = {}
        for v in H.values():
            P[ v[ NAME_STR ] ] = {
                IP_STR: v[ IP_STR ],
                MAC_STR: v[ MAC_STR ],
                COM_STR: v[ COM_STR ],
                PKT_STR: v[ PKT_STR ]
            }
        
        return P

    def get_topo_json( 
        self, P: Dict[ str, Dict ], f:str 
    ) -> None:
        """
        {
            "hosts": {
                "host_name": {
                        "ip": str,
                        "mac": str,
                        "commands": [ str ],
                        "pkts": {
                            "id": {
                                "dstAddr": str,
                                "dstMac": str,
                                "payload": str
                            }
                        }
                }
            },
            "switches": {
                "switch_name": {}
            },
            "links": [ 
                [ "host_name", "switch_port_of_host" ]
            ]
        }
        """
        H:Dict[ str, Dict ] = {}
        id:int = 1 # host id
        S = { "s1": {} }
        L:List[ List ] = []

        M = { 
            "192.168.137.5": "08:00:00:00:01:11", 
            "192.168.137.249": "08:00:00:00:02:22"
        }

        self.__add_host( H, L, id, "10.230.195.161", "A0:36:BC:D1:8D:82" )

        # k -> pkt id
        for k in P.keys():
            v:Dict[ str, str ] = P.get( k )
            sa:str = v.get( csvparaser.SRC_ADDR_STR ) # src addr
            sm:str = M[ sa ]
            da:str = v.get( csvparaser.DST_ADDR_STR ) # dst addr
            dm:str = M[ da ]

            assert sa is not da
            assert sm is not dm

            if H.get( sa ) is None:
                id = id + 1
                self.__add_host_pkt( H, L, id, sa, da, sm, dm, k )
            else:
                self.__add_pkt( H[ sa ], da, dm, k )

            if H.get( da ) is None:
                id = id + 1
                self.__add_host( H, L, id, da, dm )

        self.__write_to_file( self.__generate_topo_json( self.__convert( H ), S, L ), f )


class Tester:
    def test1( self ) -> None:
        H = {}
        S = {}
        L = []
        # ( hn, hc ) = __get_host_json( "h1", "10.0.1.1/24", "08:00:00:00:01:11", ["route add default gw 10.0.1.10 dev eth0"] )
        # H[ hn ] = hc
        # ( hn, hc ) = __get_host_json( "h2", "10.0.2.2/24", "08:00:00:00:02:22", ["route add default gw 10.0.2.20 dev eth0"] )
        # H[ hn ] = hc
        # ( hn, hc ) = __get_host_json( "h3", "10.0.3.3/24", "08:00:00:00:03:33", ["route add default gw 10.0.3.30 dev eth0"] )
        # H[ hn ] = hc
        # ( hn, hc ) = __get_host_json( "h4", "10.0.4.4/24", "08:00:00:00:04:44", ["route add default gw 10.0.4.40 dev eth0"] )
        # H[ hn ] = hc
        # S[ "s1" ] = {}
        # L.append( ["h1", "s1-p1"] )
        # L.append( ["h2", "s1-p2"] )
        # L.append( ["h3", "s1-p3"] )
        # L.append( ["h4", "s1-p4"] )
        # print( __generate_topo_json( H, S, L ) )
        # __write_to_file( __generate_topo_json( H, S, L ), "../pod-topo/topology.json" )


    def test2( self ) -> None:
        cf:str = "../test/test_csv1_small.csv"
        cf = "../test/test_csv1.csv"
        # cf = "../test/test_csv1_small_one_side_sending.csv"
        P:Dict = csvparaser.parse( cf )
        CSVParaser().get_topo_json( P, "../pod-topo/topology.json" )


if __name__ == '__main__':
    # Tester().test1()
    Tester().test2()
    pass