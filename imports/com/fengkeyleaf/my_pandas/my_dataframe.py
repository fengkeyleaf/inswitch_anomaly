# -*- coding: utf-8 -*-

from pandas import (
    DataFrame
)

"""
file: .py
description:
language: python3 3.11.3
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.size.html#pandas.DataFrame.size
# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.columns.html#pandas.DataFrame.columns
def get_row_size( d: DataFrame ) -> int:
    assert int( d.size / d.columns.size ) == d.size // d.columns.size
    return d.size // d.columns.size

