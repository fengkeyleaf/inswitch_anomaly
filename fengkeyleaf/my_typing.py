# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging

__version__ = "1.0"

l: logging.Logger = my_logging.get_logger( logging.INFO )


def equals( e1, e2 ) -> bool:
    """
    Determine if the two elements are equal or not.
    @param e1:
    @param e2:
    @return:
    """
    if type( e1 ) != type( e2 ):
        l.warning( "Type not the same: %s | %s" % ( type( e1 ), type( e2 ) ) )
        return False

    return e1 == e2


def is_same_key( D: Dict[ Any, Any ], k: Any ) -> bool:
    if not has_same_key( D ):
        l.warning( "Key types in the dict are not all identical." )

    return type( next( iter( D ) ) ) == type( k )


def has_same_key( D: Dict[ Any, Any ] ) -> bool:
    t: Any = None
    for k in D:
        if t is None:
            t = k
            continue

        if type( k ) != type( t ):
            return False

    return True
