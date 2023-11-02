# -*- coding: utf-8 -*-

import json
from typing import Dict

"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"


def load( fp: str ) -> Dict:
    """
    Load json data from a json file.
    @param fp:
    @return:
    """
    with open( fp, "r" ) as f:
        return json.load( f )
