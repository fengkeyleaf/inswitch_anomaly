from argparse import (
    ArgumentParser
)
from typing import (
    Dict
)

"""
file:
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

class MyArgParser:
    def __init__( self ) -> None:
        self.parser:ArgumentParser = ArgumentParser()

    # https://www.programiz.com/python-programming/args-and-kwargs
    def add( self, args:Dict ) -> None:
        pass

    def parse( self ) -> Dict:
        return self.parser.parse_args()
