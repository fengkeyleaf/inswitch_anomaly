# -*- coding: utf-8 -*-

from typing import Callable, Any, Type
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
def deprecated( func: Callable ) -> Callable:
    """
    Deprecated annotation.

    Usage:
    from fengkeyleaf import annotations
    @annotations.deprecated
    def your_function():
        your_code;

    @param func:
    @return:
    """
    def wrapper( *args, **kwargs ) -> Any:
        warnings.warn( func.__name__ + " is deprecated.", category = DeprecationWarning, stacklevel = 2 )
        return func( *args, **kwargs )

    return wrapper


def interface( t: Any ) -> Any:
    """
    Interface annotation.
    @param t:
    @return:
    """
    return t


def override( func: Callable ) -> Callable:
    """
    Override annotation.
    @param func:
    @return:
    """
    return func


def abstract_method( func: Callable ) -> Callable:
    """
    Abstract method annotation.
    @param func:
    @return:
    """
    return func


def abstract_class( t: Any ) -> Any:
    """
    Abstract class annotation.
    @param t:
    @return:
    """
    return t


@abstract_class
class _Tester:
    @deprecated
    def test_depre( self ):
        print( "@deprecated" )

    @interface
    def test_inter( self ):
        print( "@interface" )


if __name__ == '__main__':
    _Tester().test_depre()
    _Tester().test_inter()
