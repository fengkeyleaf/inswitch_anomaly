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
    Write data ( in the form of string ) into file.
    @param fp:
    @param d:
    """
    if fp is None or fp == "":
        l.warning( "Output file path doesn't exit: " + str( fp ) )
        return
    
    with open( fp, "w+" ) as f:
        f.write( d )


# https://www.geeksforgeeks.org/python-program-to-get-the-file-name-from-the-file-path/
def get_dir( fp: str ) -> str:
    """
    Get the directory from a file path.
    @param fp:
    @return:
    """
    return os.path.dirname( fp )


# https://note.nkmk.me/en/python-os-basename-dirname-split-splitext/
def get_filename( fp: str ) -> str:
    """
    Get the filename from a file path.
    @param fp:
    @return:
    """
    return os.path.splitext( os.path.basename( fp ) )[ 0 ]


# TODO: Valid file path format check.
def get_extension( fp: str ) -> str:
    """
    Get file extension from a file path.
    @param fp:
    @return: .file_extension
    """
    return os.path.splitext( fp )[ 1 ]


def make_dir( d: str ) -> None:
    """
    Create a directory if it doesn't exist.
    @param d:
    """
    if not os.path.isdir( d ):
        os.mkdir( d )

