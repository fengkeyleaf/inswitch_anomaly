# -*- coding: utf-8 -*-

import unittest
from typing import (
    List,
    Callable,
    Any,
    Tuple
)

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"


def find_min( L: List[ Any ], k: Callable = lambda x: x ) -> Any:
    """
    Find the min value in the list, L.
    @param L:
    @param k:
    @return:
    """
    if L is None or len( L ) <= 0: return None
    return min( L, key = k )


def find_max( L: List[ Any ], k: Callable = lambda x: x ) -> Any:
    """
    Find the max value in the list, L.
    @param L:
    @param k:
    @return:
    """
    if L is None or len( L ) <= 0: return None
    return max( L, key = k )


class _Tester( unittest.TestCase ):

    @unittest.skip
    def test_find_basic( self ):
        print()
        L: List[ int ] = [ 4, 3, 5, 6, 7, 8 ]
        print( find_min( L ) )
        print( find_max( L ) )
        L = []
        print( find_min( L ) )
        print( find_max( L ) )
        L = None
        print( find_min( L ) )
        print( find_max( L ) )

    def test_find_tuple( self ):
        print()
        L: List[ Tuple[ int, int ] ] = [ ( 1, 1 ), ( 3, 3 ), ( 5, 5 ), ( 6, 6 ), ( 9, 9 ), ( 2, 2 ) ]
        print( find_min( L, lambda x : x[ 0 ] ) )
        print( find_max( L, lambda x : x[ 0 ] ) )


if __name__ == '__main__':
    unittest.main()
