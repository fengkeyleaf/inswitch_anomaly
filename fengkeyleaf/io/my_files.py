# -*- coding: utf-8 -*-

import os
from typing import List, Iterator, Tuple

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
JSON_EXTENSION: str = ".json"


def get_files_in_dir( dir: str ) -> List[ str ]:
    """
    Find all file paths in a directory.
    @param dir:
    @return:
    """
    if dir is None or dir == "": return [];

    R: List[ str ] = []
    # https://docs.python.org/3/library/os.html#os.walk
    # https://stackoverflow.com/questions/11968976/list-files-only-in-the-current-directory
    # root, dirs, files
    it: Iterator[ Tuple[ str, List[ str ], List[ str ] ] ] = os.walk( dir )
    for s, d, F in it:
        for f in F:
            R.append( os.path.join( s, f ) )

    return R


def get_files_in_dirs( D: List[ str ] ) -> List[ List[ str ] ]:
    """
    Find all file paths in multiple directories.
    @param D:
    @return:
    """
    if D is None: return [];

    R: List[ List[ str ] ] = []
    for d in D: R.append( get_files_in_dir( d ) );
    return R
