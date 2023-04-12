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