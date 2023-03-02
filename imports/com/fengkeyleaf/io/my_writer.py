"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

def write_to_file( fp:str, d:str ) -> None:
    with open( fp, "w+" ) as f:
        f.write( d )


if __name__ == '__main__':
    pass