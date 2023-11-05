# -*- coding: utf-8 -*-

import pytest

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

from fengkeyleaf.inswitch_anomaly import sketch_write


# TODO: Move into inswitch_anomaly package.
# pytest -n auto -s -q test_sketch.py
# https://www.digitalocean.com/community/tutorials/python-unittest-unit-test-example
class Tester:
    IS_NOT_BALANCING: bool = False
    IS_WRITING: bool = True
    SKETCH_LIMITATION: int = -1

    @pytest.mark.skip
    def test_bot_lot( self ) -> None:
        dir = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/re-formatted"
        pdir = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/"

        sketch_write.SketchWriter( dir, pdir, Tester.IS_NOT_BALANCING, Tester.SKETCH_LIMITATION, Tester.IS_WRITING, 10 ).train()

    @pytest.mark.skip
    def test_ton_lot( self ):
        dir: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/re-formatted"
        pdir: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/"

        sketch_write.SketchWriter( dir, pdir, Tester.IS_NOT_BALANCING, Tester.SKETCH_LIMITATION, Tester.IS_WRITING, 10 ).train()

    # @pytest.mark.skip
    def test_unsw_nb15( self ):
        dir: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/re-formatted"
        pdir: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/"

        sketch_write.SketchWriter( dir, pdir, True, Tester.SKETCH_LIMITATION, Tester.IS_WRITING, 10 ).train()
