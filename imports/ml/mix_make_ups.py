# -*- coding: utf-8 -*-

import pandas
import sys

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

sys.path.append( "../" )
import csvparaser

class Mixer:
    def __init__( self, O: pandas.DataFrame, M: pandas.DataFrame ):
        self.O: pandas.DataFrame = O
        self.M: pandas.DataFrame = M


    # https://pandas.pydata.org/docs/reference/api/pandas.concat.html
    def mix( self ):
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.sort_values.html#pandas.DataFrame.sort_values
        return pandas.concat( [ self.O, self.M ] ).sort_values( csvparaser.TIMESTAMP_STR )