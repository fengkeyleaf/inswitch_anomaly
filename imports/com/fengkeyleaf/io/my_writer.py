# -*- coding: utf-8 -*-

import os
import logging

"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf.logging import my_logging

__version__ = "1.0"


l: logging.Logger = my_logging.get_logger( logging.INFO )


def write_to_file( fp: str, d: str ) -> None:
    """
    Write data to a file
    @param fp: Output file path.
    @param d: Data to be written.
    @return:
    """
    if not os.path.exists( fp ):
        l.warning( "File or directory is not invalid: " + fp )
        return

    with open( fp, "w+" ) as f:
        f.write( d )


# https://www.geeksforgeeks.org/python-program-to-get-the-file-name-from-the-file-path/
def get_dir( fp: str ) -> str:
    return os.path.dirname( fp )


# https://note.nkmk.me/en/python-os-basename-dirname-split-splitext/
def get_filename( fp: str ) -> str:
    return os.path.splitext( os.path.basename( fp ) )[ 0 ]


def make_dir( d: str ) -> None:
    if not os.path.isdir( d ):
        os.mkdir( d )


if __name__ == '__main__':
    pass
