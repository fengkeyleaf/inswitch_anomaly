import sys
import json
from typing import Dict, Any, List
import re
import logging

"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.inswitch_anomaly import topo
from fengkeyleaf.logging import my_logging

__version__ = "1.0"

l: logging.Logger = my_logging.get_logger( logging.INFO )


# Reference material about basic decision-tree combing packet re-forwading:
# https://github.com/cucl-srg/IIsy

#######################
# Add match-table units.
#######################

# TODO: read only once
def get_paras( fp: str ) -> Dict:
    para: Dict[ int, Dict ] = { 0: { } }
    with open( fp, "r" ) as f:
        H: Dict = json.load( f )[ "hosts" ]
        # TODO: check duplicate macs
        for k in H.keys():
            assert re.match( r"^h\d+$", k ) is not None
            assert para.get( int( k[ 1: ] ) ) is None
            para[ int( k[ 1: ] ) ] = {
                "dstAddr": H[ k ][ topo.MAC_STR ],
                "port": int( k[ 1: ] )
            }

    return para


# TODO: relative path( para ) to the config json file.
# Ipv4 forwarding rules.
def get_actionpara( action: int ) -> Dict:
    """"
    {
        port_No.: { dstAddr, port_No. }
    }
    """
    para = get_paras( "./pod-topo/topology.json" )

    assert para.get( action ) is not None, str( action ) + " | " + str( para )
    return para[ action ]


def write_forwarding_rules( p4info_helper, sw, range, port ) -> None:
    para = get_actionpara( port )
    # print( range, para )
    table_entry = p4info_helper.buildTableEntry(
        table_name = "MyIngress.ipv4_lpm",
        match_fields = {
            "hdr.ipv4.dstAddr": range
        },
        action_name = "MyIngress.ipv4_forward",
        action_params = para
    )
    sw.WriteTableEntry( table_entry )
    # print("Installed forwarding rule on %s" % sw.name)


# Decision tree rules.

def write_action_rule( switch, p4info_helper, a, b, c, d, action, port ):
    # para = get_actionpara( port )
    if port == 0:
        para: Dict = {}
    else:
        assert port == 1
        para: Dict[ str, Any ] = {
            "dstAddr": "A0:36:BC:D1:8D:82",
            "port": 1
        }

    table_entry = p4info_helper.buildTableEntry(
        table_name = "MyIngress.decision_tree",
        match_fields = {
            "meta.src_count_select": a,
            "meta.src_tls_select": b,
            "meta.dst_count_select": c,
            "meta.dst_tls_select": d,
        },
        action_name = action,
        action_params = para,
        # priority is required, otherwise gRPC unknown error.
        # https://forum.p4.org/t/p4-match-action-tables-with-range-as-the-match-kind/151/5
        priority = 1
    )
    switch.WriteTableEntry( table_entry )
    # print("Installed action rule on %s" % switch.name)


def write_feature_rule(
        switch, p4info_helper,
        t_n: str, m_n: str, a_n: str, a_param_n: str,
        range: List[ int ], ind: int
) -> None:
    """

    @param p4info_helper:
    @param switch:
    @param t_n: Table name.
    @param m_n: Match fields name.
    @param a_n: Action name.
    @param a_param_n: Action parameter names.
    @param range: parameter range.
    @param ind: Range match value.
    """
    table_entry = p4info_helper.buildTableEntry(
        table_name = t_n,
        match_fields = {
            m_n: range
        },
        action_name = a_n,
        action_params = {
            a_param_n: ind,
        },
        priority = 1
    )
    switch.WriteTableEntry( table_entry )
    # print("Installed feature1 rule on %s" % switch.name)


#
# Print out a switch information.
#

def readTableRules( p4info_helper, sw ):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print( '\n----- Reading tables rules for %s -----' % sw.name )
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            table_name = p4info_helper.get_tables_name( entry.table_id )
            print( '%s: ' % table_name, end = ' ' )
            for m in entry.match:
                print( p4info_helper.get_match_field_name( table_name, m.field_id ), end = ' ' )
                print( '%r' % (p4info_helper.get_match_field_value( m ),), end = ' ' )
            action = entry.action.action
            action_name = p4info_helper.get_actions_name( action.action_id )
            print( '->', action_name, end = ' ' )
            for p in action.params:
                print( p4info_helper.get_action_param_name( action_name, p.param_id ), end = ' ' )
                print( '%r' % p.value, end = ' ' )
            print()


def printGrpcError( e ):
    print( "gRPC Error:", e.details(), end = ' ' )
    status_code = e.code()
    print( "(%s)" % status_code.name, end = ' ' )
    traceback = sys.exc_info()[ 2 ]
    print( "[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno) )


#######################
# Writing process.
#######################

def write_basic_forwarding_rules( p4info_helper, s1 ):
    R = [ ("10.0.1.1", 32), ("10.0.2.2", 32), ("10.0.3.3", 32), ("10.0.4.4", 32) ]
    P = [ 1, 2, 3, 4 ]
    for i in range( len( R ) ):
        print( R[ i ], P[ i ] )
        write_forwarding_rules( p4info_helper, s1, R[ i ], P[ i ] )


def _process_fea_map( F: List[ List[ int ] ], i: int ) -> List[ int ]:
    L = F[ i ]
    id = len( L ) - 1
    del L[ 1 : id ]
    if len( L ) == 1:
        L.append( L[ 0 ] )

    return [ i + 1 for i in L ]


def _write_actions(
        s1, p4info_helper,
        srcCountMap, srcTLSMap, dstCountMap, dstTLSMap,
        classfication, action,
        is_debug_mode: bool
) -> None:
    for i in range( len( classfication ) ):
        a = _process_fea_map( srcCountMap, i )
        b = _process_fea_map( srcTLSMap, i )
        c = _process_fea_map( dstCountMap, i )
        d = _process_fea_map( dstTLSMap, i )

        ind = int( classfication[ i ] )
        ac = action[ ind ]
        if ac == 0:
            l.debug( "A: a=%s,b=%s,c=%s,d=%s,ac=%s,ac=%d" % ( a, b, c, d, "MyIngress.drop", ac ) )
            if not is_debug_mode: write_action_rule( s1, p4info_helper, a, b, c, d, "MyIngress.drop", 0 );
        else:
            l.debug( "A: a=%s,b=%s,c=%s,d=%s,ac=%s,ac=%d" % ( a, b, c, d, "MyIngress.ipv4_forward", ac ) )
            if not is_debug_mode: write_action_rule( s1, p4info_helper, a, b, c, d, "MyIngress.ipv4_forward", ac );


M: int = 0xffff


def _write_fea_rules(
    s1, p4info_helper,
    t_n, m_n, a_n, a_param_n,
    F: List[ int ], is_debug_mode: bool
):
    """

    @param s1:
    @param p4info_helper:
    @param t_n: Table name.
    @param m_n: Match fields name.
    @param a_n: Action name.
    @param a_param_n: Action parameter names.
    @param F: List of feature values.
    @param is_debug_mode:
    """
    if len( F ) != 0:
        F.append( 0 )
        F.append( M )
        F.sort()
        for i in range( len( F ) - 1 ):
            l.debug( "%s: range=%s,ind=%s" % ( t_n, F[ i: i + 2 ], i + 1 ) )
            if not is_debug_mode:
                write_feature_rule( s1, p4info_helper, t_n, m_n, a_n, a_param_n, F[ i: i + 2 ], i + 1 )

        return

    l.debug( "%s: range=%s,ind=%s" % ( t_n, [ 0, M ], 1 ) )
    if not is_debug_mode:
        write_feature_rule( s1, p4info_helper, t_n, m_n, a_n, a_param_n, [ 0, M ], 1 )


def write_ml_rules(
        dstTLS, srcCount, srcTLS, dstCount,
        srcCountMap, srcTLSMap, dstCountMap, dstTLSMap,
        classfication, action,
        s1 = None, p4info_helper = None,
        is_debug_mode: bool = False
):
    _write_actions( s1, p4info_helper, srcCountMap, srcTLSMap, dstCountMap, dstTLSMap, classfication, action, is_debug_mode )

    _write_fea_rules( s1, p4info_helper, "MyIngress.s.src_count_select_t", "scv", "MyIngress.s.src_count_select_a", "v", srcCount, is_debug_mode )
    _write_fea_rules( s1, p4info_helper, "MyIngress.s.src_tls_select_t", "stv", "MyIngress.s.src_tls_select_a", "v", srcTLS, is_debug_mode )
    _write_fea_rules( s1, p4info_helper, "MyIngress.s.dst_count_select_t", "dcv", "MyIngress.s.dst_count_select_a", "v", dstCount, is_debug_mode )
    _write_fea_rules( s1, p4info_helper, "MyIngress.s.dst_tls_select_t", "dtv", "MyIngress.s.dst_tls_select_a", "v", dstTLS, is_debug_mode )

    # readTableRules(p4info_helper, s1)
    l.info( "Done with injecting routing rules" )
