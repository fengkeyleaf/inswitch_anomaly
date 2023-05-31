# -*- coding: utf-8 -*-
import unittest
from typing import (
    Dict,
    Tuple,
    Callable
)

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"


def find_min_value( D: Dict, k: Callable = lambda x: x[ 1 ] ) -> Tuple:
    """
    Find the key-value pair in this dict with the min value
    @param D:
    @param k: lambda to find the min value in this dict,
              By default, it will compare values of this dict so that
              the type of the value should be either a naive type, like int,
              or explicitly pass a comparator.
    @return: ( k, v ), where v is the min one in this dict.
    """
    return min( D.items(), key = k )


def find_max_value( D: Dict, k: Callable = lambda x: x[ 1 ] ) -> Tuple:
    return max( D.items(), key = k )


class _Tester( unittest.TestCase ):
    COUNT_STR = "count"
    TLS_STR = "tls"

    def test_find_m_value( self ):
        D: Dict[ str, Dict[ str, int ] ] = {
            "a": {
                _Tester.COUNT_STR: "1",
                _Tester.TLS_STR: "1"
            },
            "b": {
                _Tester.COUNT_STR: "2",
                _Tester.TLS_STR: "2"
            },
            "c": {
                _Tester.COUNT_STR: "3",
                _Tester.TLS_STR: "3"
            }
        }

        print( find_max_value( D, lambda p : p[ 1 ][ _Tester.COUNT_STR ] ) )
        print( find_max_value( D, lambda p : p[ 1 ][ _Tester.TLS_STR ] ) )
        print( find_min_value( D, lambda p : p[ 1 ][ _Tester.TLS_STR ] ) )
        print( find_min_value( D, lambda p : p[ 1 ][ _Tester.COUNT_STR ] ) )


if __name__ == '__main__':
    unittest.main()
