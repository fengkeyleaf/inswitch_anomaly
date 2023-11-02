# -*- coding: utf-8 -*-

import warnings

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"


# https://blog.csdn.net/u013632755/article/details/106066972
def deprecated( func ):
    def wrapper( *args, **kwargs ):
        warnings.warn( func.__name__ + " is deprecated.", category = DeprecationWarning, stacklevel = 2 )
        return func( *args, **kwargs )

    return wrapper


class _Tester:
    @deprecated
    def test( self ):
        pass


if __name__ == '__main__':
    _Tester().test()
