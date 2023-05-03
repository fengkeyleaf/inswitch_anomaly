# -*- coding: utf-8 -*-

import logging

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""


def getLogger( ll: int ) -> logging.Logger:
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