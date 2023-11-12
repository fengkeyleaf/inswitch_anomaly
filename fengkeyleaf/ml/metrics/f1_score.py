# -*- coding: utf-8 -*-

from typing import List, Tuple

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"


# Reference materials:
# https://www.educative.io/answers/what-is-a-confusion-matrix
# https://www.educative.io/answers/what-is-the-f1-score
# https://www.educative.io/answers/what-is-precision-and-recall
class F1Score:
    def __init__( self ) -> None:
        self._tp: int = 0
        self._fp: int = 0
        self._tn: int = 0
        self._fn: int = 0

        self.acc: float = -1
        self.pre: float = -1
        self.re: float = -1
        self.f1: float = -1

        self._y_true: List[ int ] = []
        self._y_pre: List[ int ] = []

    def add_tp( self ) -> None:
        self._tp += 1

    def get_tp( self ) -> int:
        return self._tp

    def add_fp( self ) -> None:
        self._fp += 1

    def get_fp( self ) -> int:
        return self._fp

    def add_tn( self ) -> None:
        self._tn += 1

    def get_tn( self ) -> int:
        return self._tn

    def add_fn( self ) -> None:
        self._fn += 1

    def get_fn( self ) -> int:
        return self._fn

    def get_trues( self ) -> int:
        return self._tp + self._tn

    def get_total( self ) -> int:
        return self._tp + self._tn + self._fp + self._fn

    def reset( self ) -> None:
        self._tp = self._fp = self._fn = self._tn = -1
        self.acc = self.pre = self.re = self.f1 = -1

    def cal( self ) -> None:
        self.acc = self.get_trues() / self.get_total()
        self.pre = self._tp / ( self._tp + self._fp )
        self.re = self._tp / ( self._tp + self._fn )
        self.f1 = 2 * ( self.pre * self.re ) / ( self.pre + self.re )

    def add_y( self, y_t: int, y_p: int ) -> None:
        self._y_true.append( y_t )
        self._y_pre.append( y_p )

    def get_y( self ) -> Tuple[ List[ int ], List[ int ] ]:
        assert len( self._y_true ) == len( self._y_pre )
        return self._y_true, self._y_pre
