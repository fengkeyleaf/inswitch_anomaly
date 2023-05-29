import os

"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"


def write_to_file( fp: str, d: str ) -> None:
    """
    Write data ( in the form of string ) into file.
    @param fp:
    @param d:
    """
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

