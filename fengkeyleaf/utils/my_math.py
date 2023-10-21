# -*- coding: utf-8 -*-

from typing import List

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

# Max value for a 32-bit signed integer.
MAX_SIGNED_32_BIT_INT: int = 2 ** 31 - 1


def find_median( N: List[ float ] ) -> float:
    """
    Find the median in the list of numbers.
    @param N:
    @return:
    """
    if N is None or len( N ) <= 0: return None

    N = sorted( N )
    l = len( N )
    # Odd length
    if l % 2 == 1:
        return N[ l // 2 ]

    # Even length
    mid_right = l // 2
    return ( N[ mid_right - 1 ] + N[ mid_right ] ) / 2.0


def assert_overflow( n: float, r: float ) -> bool:
    return ( n >= 0 and r >= 0 ) or ( n <= 0 and r <= 0 )