import re
from typing import List

"""
file: ml.py
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
"""

# Reference material about basic decision-tree combing packet re-forwading:
# https://github.com/cucl-srg/IIsy

#######################
# Paraphrase the decision tree txt file.
#######################

def find_action( textfile:str ) -> List[ int ]:
    action = []
    f = open(textfile)
    for line in f:
        n = re.findall(r"class", line)
        if n:
            fea = re.findall(r"\d", line)
            action.append(int(fea[1]))
    f.close()
    return action


def find_feature( tf, n ):
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

    # https://docs.python.org/3.8/library/functions.html#map
    # https://www.geeksforgeeks.org/python-map-function/
    r = map( lambda l : [ int( i ) for i in l ], F )
    return ( e for e in r )


def find_classification( tf, F, FS, fr ):
    """
    :param tf: decision tree txt file.
    :param F: list of features.
    :param FS: list of feature names in string.
    :param fr: regular exp of feature names.
    :return: ( feature1, feature2, ..., featureN, classfication )
    """
    fea = []
    sign = []
    num = []
    with open( tf, "r" ) as f:
        for line in f:
            n = re.findall( r"when", line )
            if n:
                fea.append( re.findall( fr, line ) )
                sign.append( re.findall( r"(<=|>)", line ) )
                num.append( re.findall( r"\d+\.?\d*", line ) )

    FL = [ [] for _ in range( len( F ) + 1 ) ]

    for i in range( len( fea ) ):
        FLT = [ [ k for k in range( len( f ) + 1 ) ] for f in F ]
        assert len( FLT ) == len( FS ), str( len( FLT ) ) + " " + str( len( FS ) )
        assert len( FS ) == len( F )

        for j, feature in enumerate( fea[ i ] ):
            for k in range( len( FS )):
                if feature == FS[ k ]:
                    sig = sign[ i ][ j ]
                    thres = int( float( num[ i ][ j ] ) )
                    id = F[ k ].index( thres )
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