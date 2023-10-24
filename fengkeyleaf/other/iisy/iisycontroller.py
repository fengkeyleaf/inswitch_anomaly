# -*- coding: utf-8 -*-

import sys
import os
import re
import logging

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# fengkeyleaf imports
# Add path dependency, which is allowed to directly exclude this file from the working directory.
sys.path.append(
    os.path.join(
        os.path.dirname( os.path.abspath(__file__) ),
        '../../'
    )
)
from fengkeyleaf.logging import my_logging
from fengkeyleaf.inswitch_anomaly import p4ml, write_rules

__version__ = "1.0"


l: logging.Logger = my_logging.get_logger( logging.INFO )


# Reference materials:
# https://github.com/cucl-srg/IIsy/blob/master/iisy_sw/simple_example/decision_tree/mycontroller.py
class IIsyController:
    """
    Test to see if my own modified version is correct or not.
    """
    def __init__( self ):
        pass

    @staticmethod
    def find_feature( textfile ):
        f = open( textfile )
        line = f.readline()
        proto = re.findall( '\d+', line )
        line = f.readline()
        src = re.findall( '\d+', line )
        line = f.readline()
        dst = re.findall( '\d+', line )
        f.close()
        proto = [ int( i ) for i in proto ]
        src = [ int( i ) for i in src ]
        dst = [ int( i ) for i in dst ]
        return proto, src, dst

    @staticmethod
    def find_classification( textfile, proto, src, dst ):
        fea = [ ]
        sign = [ ]
        num = [ ]
        f = open( textfile, 'r' )
        for line in f:
            n = re.findall( r"when", line )
            if n:
                fea.append( re.findall( r"(proto|src|dst)", line ) )
                sign.append( re.findall( r"(<=|>)", line ) )
                num.append( re.findall( r"\d+\.?\d*", line ) )
        f.close()

        protocol = [ ]
        srouce = [ ]
        dstination = [ ]
        classfication = [ ]

        for i in range( len( fea ) ):
            feature1 = [ k for k in range( len( proto ) + 1 ) ]
            feature2 = [ k for k in range( len( src ) + 1 ) ]
            feature3 = [ k for k in range( len( dst ) + 1 ) ]
            for j, feature in enumerate( fea[ i ] ):
                if feature == 'proto':
                    sig = sign[ i ][ j ]
                    thres = int( float( num[ i ][ j ] ) )
                    id = proto.index( thres )
                    if sig == '<=':
                        while id < len( proto ):
                            if id + 1 in feature1:
                                feature1.remove( id + 1 )
                            id = id + 1
                    else:
                        while id >= 0:
                            if id in feature1:
                                feature1.remove( id )
                            id = id - 1
                elif feature == 'src':
                    sig = sign[ i ][ j ]
                    thres = int( float( num[ i ][ j ] ) )
                    id = src.index( thres )
                    if sig == '<=':
                        while id < len( src ):
                            if id + 1 in feature2:
                                feature2.remove( id + 1 )
                            id = id + 1
                    else:
                        while id >= 0:
                            if id in feature2:
                                feature2.remove( id )
                            id = id - 1
                else:
                    sig = sign[ i ][ j ]
                    thres = int( float( num[ i ][ j ] ) )
                    id = dst.index( thres )
                    if sig == '<=':
                        while id < len( dst ):
                            if id + 1 in feature3:
                                feature3.remove( id + 1 )
                            id = id + 1
                    else:
                        while id >= 0:
                            if id in feature3:
                                feature3.remove( id )
                            id = id - 1
            protocol.append( feature1 )
            srouce.append( feature2 )
            dstination.append( feature3 )
            a = len( num[ i ] )
            classfication.append( num[ i ][ a - 1 ] )
        return (protocol, srouce, dstination, classfication)

    @staticmethod
    def find_action( textfile ):
        action = [ ]
        f = open( textfile )
        for line in f:
            n = re.findall( r"class", line )
            if n:
                fea = re.findall( r"\d", line )
                action.append( int( fea[ 1 ] ) )
        f.close()
        return action

    @staticmethod
    def write_rules(
            protocol, srouce, dstination, classfication, action,
            proto, src, dst
    ):
        for i in range( len( classfication ) ):
            a = protocol[ i ]
            id = len( a ) - 1
            del a[ 1:id ]
            if (len( a ) == 1):
                a.append( a[ 0 ] )
            b = srouce[ i ]
            id = len( b ) - 1
            del b[ 1:id ]
            if (len( b ) == 1):
                b.append( b[ 0 ] )
            c = dstination[ i ]
            id = len( c ) - 1
            del c[ 1:id ]
            if (len( c ) == 1):
                c.append( c[ 0 ] )

            ind = int( classfication[ i ] )
            ac = action[ ind ]
            a = [ i + 1 for i in a ]
            b = [ i + 1 for i in b ]
            c = [ i + 1 for i in c ]

            if ac == 0:
                l.info( "A: a=%s,b=%s,c=%s,ac=%s,ac=%d" % (a, b, c, "MyIngress.drop", ac) )
            else:
                l.info( "A: a=%s,b=%s,c=%s,ac=%s,ac=%d" % (a, b, c, "MyIngress.ipv4_forward", ac) )

        if len( proto ) != 0:
            proto.append( 0 )
            proto.append( 32 )
            proto.sort()
            for i in range( len( proto ) - 1 ):
                l.info( "F1: range=%s,ind=%s" % (proto[ i:i + 2 ], i + 1) )
        else:
            l.info( "F1: range=%s,ind=%s" % ([ 0, 32 ], 1) )

        if len( src ) != 0:
            src.append( 0 )
            src.append( 65535 )
            src.sort()
            for i in range( len( src ) - 1 ):
                l.info( "F2: range=%s,ind=%s" % (src[ i:i + 2 ], i + 1) )
        if len( dst ) != 0:
            dst.append( 0 )
            dst.append( 65535 )
            dst.sort()
            for i in range( len( dst ) - 1 ):
                l.info( "F3: range=%s,ind=%s" % (dst[ i:i + 2 ], i + 1) )

    def process( self, inputfile, actionfile ):
        proto, src, dst = IIsyController.find_feature( inputfile )
        l.info( "proto=%s\nsrc=%s\ndst=%s" % (proto, src, dst) )
        protocol, srouce, dstination, classfication = IIsyController.find_classification( inputfile, proto, src, dst )
        l.info( "protocol=%s\nsrouce=%s\ndstination=%s\nclassfication=%s" % ( protocol, srouce, dstination, classfication ) )
        action = IIsyController.find_action( actionfile )

        IIsyController.write_rules(
            protocol, srouce, dstination, classfication, action,
            proto, src, dst
        )

        l.info( "------------------------" )


class MyController:
    """
    Test myController.py and related functions.
    """
    def __init__( self ):
        pass

    def process( self, inputfile, actionfile ) -> None:
        fr = r"(srcCount|srcTLS|dstCount|dstTLS)"
        FS = [ "srcCount", "srcTLS", "dstCount", "dstTLS" ]

        srcCount, srcTLS, dstCount, dstTLS = p4ml.find_feature( inputfile, len( FS ) )
        l.info( "Feature:\nsrcCount=%s,\nsrcTLS=%s,\ndstCount=%s,\n dstTLS=%s" % (srcCount, srcTLS, dstCount, dstTLS) )
        srcCountMap, srcTLSMap, dstCountMap, dstTLSMap, classfication = p4ml.find_classification(
            inputfile,[ srcCount, srcTLS, dstCount, dstTLS ], FS, fr
        )
        l.info( "Classification:\nsrcCountMap=%s,\nsrcTLSMap=%s,\ndstCountMap=%s,\ndstTLSMap=%s,\nclass=%s" % (
            srcCountMap, srcTLSMap, dstCountMap, dstTLSMap, classfication) )
        action = p4ml.find_action( actionfile )
        l.info( "Action: %s" % ( action ) )

        write_rules.l.setLevel( logging.DEBUG )
        write_rules.write_ml_rules(
            srcCount = srcCount,
            srcCountMap = srcCountMap,
            srcTLS = srcTLS,
            srcTLSMap = srcTLSMap,
            dstCount = dstCount,
            dstCountMap = dstCountMap,
            dstTLS = dstTLS,
            dstTLSMap = dstTLSMap,
            classfication = classfication,
            action = action,
            is_debug_mode = True
        )


if __name__ == '__main__':
    f: str = "./tree.txt"
    f: str = "./tree_new.txt"
    IIsyController().process( f, "./action.txt" )

    f = "./UNSW_2018_IoT_Botnet_Dataset_1_tree.txt"
    f = "./UNSW_2018_IoT_Botnet_Dataset_1_new_tree.txt"
    MyController().process( f, "./action.txt" )
