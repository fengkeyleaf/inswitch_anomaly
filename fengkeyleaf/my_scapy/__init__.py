# -*- coding: utf-8 -*-

import logging
import scapy.all

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


def get_if( target_iface: str ) -> str:
    """
    Get the target interface.
    @param target_iface: Target Interface in the interface list.
    @type target_iface: str
    @return: Name of the target interface.
    @rtype: str
    """
    # https://scapy.readthedocs.io/en/latest/api/scapy.interfaces.html#scapy.interfaces.get_if_list
    iface: str = None  # "h1-eth0"
    for i in scapy.all.get_if_list():
        if target_iface in i:
            iface = i
            break
    if not iface:
        l.error( f"Cannot find {target_iface} interface" )
        exit( 1 )

    return iface

