# -*- coding: utf-8 -*-

import re
import pandas
from typing import List

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

import fengkeyleaf.inswitch_anomaly as fkl_inswitch

__version__ = "1.0"

# Filtering functions

# An IPv4 address has the following format: x . x . x . x
# where x is called an octet and must be a decimal value between 0 and 255.
IPV4_REG = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"  # raw string


def ipv4_filter( df: pandas.DataFrame ) -> pandas.DataFrame:
    """
    Discard a pkt record with invalid IPv4 address format.
    @param df: Input DataFrame.
    @return: A modified copy of the input DataFrame.
    """
    I: List[ int ] = []
    for ( i, s ) in df.iterrows():
        if ( re.search( IPV4_REG, df.loc[ i, fkl_inswitch.SRC_ADDR_STR ] ) is None or
                re.search( IPV4_REG, df.loc[ i, fkl_inswitch.DST_ADDR_STR ] ) is None ):
            I.append( i )

    return df.drop( I )
