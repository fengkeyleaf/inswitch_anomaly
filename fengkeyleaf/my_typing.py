# -*- coding: utf-8 -*-

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"


# TODO: Use warning, not assert.
def equals( e1, e2 ) -> bool:
    """
    Assert if the two elements are the same type.
    @param e1:
    @param e2:
    @return:
    """
    assert type( e1 ) == type( e2 ), "%s | %s" % ( type( e1 ), type( e2 ) )
    return True
