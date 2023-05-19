# -*- coding: utf-8 -*-

import logging

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# https://docs.python.org/3/library/logging.html#logging-levels
def get_logger( ll: int ) -> logging.Logger:
    """

    @param ll: logging level
    @return:
    """
    logging.basicConfig( format = '%(asctime)s %(message)s' )
    # Creating an object
    l: logging.Logger = logging.getLogger()
    # Setting the threshold of l to DEBUG
    l.setLevel( ll )
    return l


def get_level_name( n: str ) -> int:
    # https://docs.python.org/3/library/logging.html#logging.getLevelName
    return logging.getLevelName( n.upper() )