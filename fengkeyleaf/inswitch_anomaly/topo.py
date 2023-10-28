# -*- coding: utf-8 -*-

import json
from typing import ( Dict, List, Tuple )

import pandas

"""
file: topo.py
description: Parse pkt csv files into a dict, or build a network topology used by P4 mininet.
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# fengkeyleaf imports
from fengkeyleaf.io import my_writer
import fengkeyleaf.inswitch_anomaly as fkl_inswitch


IP_STR = "ip"
MAC_STR = "mac"
COM_STR = "commands"
HOST_STR = "hosts"
SWITCH_STR = "switches"
LINK_STR = "links"
NAME_STR = "name"
PKT_STR = "pkts"
DST_IP_STR = "dstAddr"
DST_MAC_STR = "dstMac"


class Parser:
    """
    Parse processed pkt csv files into a dict.
    """
    def __init__( self ) -> None:
        pass

    @staticmethod
    def _assertion( a: str, m: str ) -> bool:
        D: Dict = {}
        if D.get( a ) is not None:
            assert D[ a ] == m
            return True

        D[ a ] = m
        return True

    # https://stackoverflow.com/questions/11706215/how-can-i-fix-the-git-error-object-file-is-empty/12371337#12371337
    @staticmethod
    def parse( f: str ) -> Dict[ int, Dict ]:
        """
        Class to parse processed pkt csv files into a dict.
        The file should be in the standard format, that is, all features are mapping to our own ones.
        :param f: file path to the csv file.
        :return: {
            pkt_id: {
                srcAddr: srcIP, dstAddr: dstIP,
                srcMAC: srcMac, dstMAC: dstMac,
                Label: Number( 0 or 1 )
            }
        }
        """
        dic: Dict[ int, Dict ] = {}
        id: int = 0
        # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
        # https://pandas.pydata.org/docs/reference/frame.html
        # https://www.geeksforgeeks.org/python-next-method/
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.html?highlight=series#pandas.Series
        for ( _, s ) in pandas.read_csv( f ).iterrows():
            assert dic.get( s[ fkl_inswitch.ID_STR ] ) is None, "Already seen this ID before."
            id = id + 1
            # if ( s[ ID_STR ] == 1 or s[ ID_STR ] == 2006 or s[ ID_STR ] == 2007 ):
            #     continue

            assert id <= int( s[ fkl_inswitch.ID_STR ] ) # Consistent incremental id garaunteed
            assert s[ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.GOOD_LABEL_STR ) or s[ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.BAD_LABEL_STR ), type( s[ fkl_inswitch.LABEL_STR ] )
            assert Parser._assertion( s[ fkl_inswitch.SRC_ADDR_STR ], s[ fkl_inswitch.SRC_MAC_STR ] ) and Parser._assertion( s[ fkl_inswitch.DST_ADDR_STR ], s[ fkl_inswitch.DST_MAC_STR ] )

            # print( "s=%s, d=%s" % ( s[ "Source" ], s[ "Destination" ] ) )
            dic[ s[ fkl_inswitch.ID_STR ] ] = {
                fkl_inswitch.SRC_ADDR_STR: s[ fkl_inswitch.SRC_ADDR_STR ],
                fkl_inswitch.DST_ADDR_STR: s[ fkl_inswitch.DST_ADDR_STR ],
                fkl_inswitch.SRC_MAC_STR: s[ fkl_inswitch.SRC_MAC_STR ],
                fkl_inswitch.DST_MAC_STR: s[ fkl_inswitch.DST_MAC_STR ],
                fkl_inswitch.LABEL_STR: s[ fkl_inswitch.LABEL_STR ]
            }

        print( "csvparaser: %d pkts in this csv file" % ( id ) )
        return dic


# https://www.geeksforgeeks.org/python-classes-and-objects/
# https://www.geeksforgeeks.org/g-fact-34-class-or-static-variables-in-python/
# https://www.geeksforgeeks.org/access-modifiers-in-python-public-private-and-protected/
class Builder:
    """
    Build p4 network topology json file with pkts stored in a dict..
    """
    def __init__( self ) -> None:
        self.h1: Dict = {
            NAME_STR: "h1",
            IP_STR: "10.230.195.161",
            MAC_STR: "A0:36:BC:D1:8D:82"
        }

    @staticmethod
    # https://pythonexamples.org/python-write-json-to-file/
    def __generate_topo_json( H: Dict, S: Dict, L: List ) -> str:
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

    @staticmethod
    def _write_to_file( topo, fp ):
        with open( fp, "w+" ) as f:
            f.write( topo )

    @staticmethod
    def _add_pkt( h: Dict, da: str, dm: str, id: str ):
        assert h[ PKT_STR ].get( id ) is None

        h[ PKT_STR ][ id ] = {
            DST_IP_STR: da,
            DST_MAC_STR: dm
        }

    @staticmethod
    def _add_host(
            H: Dict[ str, Dict ], L: List, id: str, a: str, m: str
    ) -> Dict:
        hn: str = "h" + id # host name
        # Initi host
        h: Dict = {
            NAME_STR: hn,
            IP_STR: a,
            MAC_STR: m,
            COM_STR: [ "route add default gw " + a + " dev eth0" ],
            PKT_STR: {}
        }

        # Add link
        L.append( [ hn, "s1-p" + str( id ) ] )

        H[ a ] = h
        return h

    def _get_host_json(
            self, n: str, i: str, m: str, c: List[ str ]
    ) -> Tuple[ str, Dict ]:
        return (
            n,
            {
                IP_STR: i,
                MAC_STR: m,
                COM_STR: c
            }
        )

    @staticmethod
    def _add_host_pkt(
            H: Dict, L: List,
            idh: str, sa: str,
            da: str, sm: str,
            dm: str, idp: str
    ) -> None:
        """
        :param H: hosts in a dict.
        :param L: list of links.
        :param idh: id of host. 
        :param sa: src addr 
        :param da: dst addr 
        :param sm: src mac 
        :param dm: dst mac
        :param idp: id of pkt
        """
        Builder._add_pkt(
            Builder._add_host( H, L, idh, sa, sm ),
            da, dm, idp
        )

    @staticmethod
    def _convert( H: Dict ) -> Dict:
        P = {}
        for v in H.values():
            P[ v[ NAME_STR ] ] = {
                IP_STR: v[ IP_STR ],
                MAC_STR: v[ MAC_STR ],
                COM_STR: v[ COM_STR ],
                PKT_STR: v[ PKT_STR ]
            }

        return P

    def _is_not_terminator_host( self, a: str, m: str ) -> bool:
        assert self.h1[ IP_STR ] != a
        assert self.h1[ MAC_STR ] != m
        return True

    def get_topo_json(
            self, P: Dict[ int, Dict ], f: str
    ) -> Dict:
        """
        Get the network topology json file from the input dict, P
        @param P: Dict to store all pkt info.
        @param f: File path to the output topology.
                  If None, will not output the result to a file.
        @return: Dict structure of the network topology:
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
                                        "label": Number( 0 or 1 )
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
        H: Dict[ str, Dict ] = {}
        id: int = 1  # host id
        S = { "s1": {} }
        L: List[ List ] = []

        M = {
            "192.168.137.5": "08:00:00:00:01:11",
            "192.168.137.249": "08:00:00:00:02:22"
        }

        Builder._add_host( H, L, str( id ), self.h1[ IP_STR ], self.h1[ MAC_STR ] )

        # k -> pkt id
        for k in P.keys():
            v: Dict[ str, str ] = P.get( k )
            sa: str = v[ fkl_inswitch.SRC_ADDR_STR ]  # src addr
            sm: str = v[ fkl_inswitch.SRC_MAC_STR ]
            da: str = v[ fkl_inswitch.DST_ADDR_STR ]  # dst addr
            dm: str = v[ fkl_inswitch.DST_MAC_STR ]

            assert sa is not da
            assert sm is not dm
            assert self._is_not_terminator_host( sa, sm ) and self._is_not_terminator_host( da, dm )

            if H.get( sa ) is None:
                id = id + 1
                Builder._add_host_pkt( H, L, str( id ), sa, da, sm, dm, str( k ) )
            else:
                Builder._add_pkt( H[ sa ], da, dm, str( k ) )

            if H.get( da ) is None:
                id = id + 1
                Builder._add_host( H, L, str( id ), da, dm )

        res: Dict = {
            HOST_STR: Builder._convert( H ),
            SWITCH_STR: S,
            LINK_STR: L
        }
        my_writer.write_to_file( f, json.dumps( res, indent = 4 ) )
        return res

    @staticmethod
    def get_host_jsons( f: str, d: Dict ) -> None:
        """
        Get host json files in the network topology.
        @param f: Output directory.
        @param d: Dict containing pkt information.
        """
        d: Dict = d[ HOST_STR ]
        for k in d:
            assert d.get( k ) is not None
            my_writer.write_to_file(
                f + k + ".json",
                json.dumps( d[ k ], indent = 4 )
            )


class _Tester:
    def test1( self ) -> None:
        H = { }
        S = { }
        L = [ ]
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
        cf: str = "../test/test_csv1_small.csv"
        cf = "../test/test_csv1.csv"
        # cf = "../test/test_csv1_small_one_side_sending.csv"
        # P:Dict = csvparaser.parse( cf )
        # CSVParaser().get_topo_json( P, "../pod-topo/topology.json" )


if __name__ == '__main__':
    # _Tester().test1()
    _Tester().test2()
