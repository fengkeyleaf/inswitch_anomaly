import re
from typing import List, Tuple, Any

"""
file: p4ml.py
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
"""

__version__ = "1.0"

# Reference material about basic decision-tree combing packet re-forwading:
# https://github.com/cucl-srg/IIsy

#######################
# Paraphrase the decision tree txt file.
#######################

def find_action( tf: str ) -> List[ int ]:
    """

    @param tf: File path to the decision tree txt file.
    @return:
    """
    A: List[ int ] = []
    with open( tf, "r" )as f:
        for line in f:
            n = re.findall( r"class", line )
            if n:
                fea = re.findall( r"\d", line )
                A.append( int( fea[ 1 ] ) )

    return A


def find_feature( tf: str, n: int ) -> Tuple:
    """
    :param tf: decision tree txt file.
    :param n: # of features.
    :return: ( feature1, feature2, ..., featureN )
    """
    # https://www.geeksforgeeks.org/with-statement-in-python/
    F = []
    with open( tf, "r" ) as f:
        for _ in range( n ):
            F.append( re.findall( '\d+', f.readline() ) )

    # print( F )
    # https://docs.python.org/3.8/library/functions.html#map
    # https://www.geeksforgeeks.org/python-map-function/
    r = map( lambda l : [ int( i ) for i in l ], F )
    return ( e for e in r )


def find_classification(
        tf: str, F: List[ List[ Any ] ], FS: List[ str ], fr: str
) -> Tuple:
    """
    :param tf: decision tree txt file.
    :param F: list of features.
    :param FS: list of feature names in string.
    :param fr: regular exp of feature names.
    :return: ( feature1, feature2, ..., featureN, classfication )
    """
    fea: List = []
    sign: List = []
    num: List = []
    with open( tf, "r" ) as f:
        for line in f:
            n = re.findall( r"when", line )
            if n:
                fea.append( re.findall( fr, line ) )
                sign.append( re.findall( r"(<=|>)", line ) )
                num.append( re.findall( r"\d+\.?\d*", line ) )


    # [ fea1, fea2, fea2, ......, feaN, classification ]
    FL: List = [ [] for _ in range( len( F ) + 1 ) ]

    # print( "fea=%s\nsign=%s\nnum=%s\nFL=%s\nFS=%s" % ( fea, sign, num, FL, FS ) )
    for i in range( len( fea ) ):
        FLT: List[ List[ int ] ] = [ [ k for k in range( len( f ) + 1 ) ] for f in F ]
        assert len( FLT ) == len( FS ), str( len( FLT ) ) + " " + str( len( FS ) )
        assert len( FS ) == len( F )

        # print( "fea[" + str( i ) + "]: " + str( fea[ i ] ) )
        for j, feature in enumerate( fea[ i ] ):
            # print( str( j ) + " " + str( feature ) )
            for k in range( len( FS ) ):
                if feature == FS[ k ]:
                    sig: str = sign[ i ][ j ]
                    thres: int = int( float( num[ i ][ j ] ) )
                    id: int = F[ k ].index( thres )
                    # print( "fea=%s, sig=%s,thres=%s,id=%s" % (feature, sig, thres, id) )

                    if sig == "<=":
                        while id < len( F[ k ] ):
                            if id + 1 in FLT[ k ]:
                                FLT[ k ].remove( id + 1 )
                            id = id + 1
                    else:
                        while id >= 0:
                            if id in FLT[ k ]:
                                FLT[ k ].remove( id )
                            id = id - 1
                # else:
                    # https://www.geeksforgeeks.org/python-assert-keyword/
                    # assert False, FS[ k ] + " " + feature
        
        for k in range( len( FL ) ):
            if ( k == len( FL ) - 1 ):
                FL[ k ].append( num[ i ][ len( num[ i ] ) - 1 ] )
            else:
                FL[ k ].append( FLT[ k ] )

    return ( e for e in FL )