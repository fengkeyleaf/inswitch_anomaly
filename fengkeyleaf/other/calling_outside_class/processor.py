# -*- coding: utf-8 -*-

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

import receiver

__version__ = "1.0"

class Processor:
    def __init__( self ):
        self.d: str = "Original"
        pass

    def process( self, p: str ):
        self.d = p

def test1():
    p: Processor = Processor()
    r: receiver.Receiver = receiver.Receiver()
    print( p.d )

    r.receive( p.process )

    print( p.d )


def test2():
    p: Processor = Processor()
    r: receiver.Receiver = receiver.Receiver( p.process )
    print( p.d )

    r.start()

    print( p.d )


if __name__ == '__main__':
    test2()
