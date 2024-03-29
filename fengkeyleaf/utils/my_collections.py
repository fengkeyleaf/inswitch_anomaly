# -*- coding: utf-8 -*-

from typing import List, Any

"""
file: .py
description:
language: python3 3.8.10
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""


# https://www.geeksforgeeks.org/python-program-to-check-if-given-array-is-monotonic/
def is_monotonic( A: List[ Any ] ) -> bool:
    """
    Is the list, A, monotonic?
    @param A:
    @return:
    """
    return ( all( A[ i ] <= A[ i + 1 ] for i in range( len( A ) - 1 ) ) or
            all( A[ i ] >= A[ i + 1 ] for i in range( len( A ) - 1 ) ) )