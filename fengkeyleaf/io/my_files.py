# -*- coding: utf-8 -*-

import os
from typing import (
    List
)

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"


# Coding
UTF8: str = "utf8"

# Error Handling
BACK_SLASH_REPLACE: str = "backslashreplace"

# File extensions in lower case
CSV_EXTENSION: str = ".csv"


def get_files_in_dir( dir: str ) -> List[ str ]:
    """
    Find all file paths in a directory.
    @param dir:
    @return:
    """
    if dir is None or dir == "": return [];

    R: List[ str ] = []
    for s, d, F in os.walk( dir ):
        for f in F:
            R.append( os.path.join( s, f ) )

    return R


def get_files_in_dirs( D: List[ str ] ) -> List[ List[ str ] ]:
    """
    Find all file paths in multiple directories.
    @param dir:
    @return:
    """
    if D is None: return [];

    R: List[ List[ str ] ] = []
    for d in D: R.append( get_files_in_dir( d ) );
    return R
