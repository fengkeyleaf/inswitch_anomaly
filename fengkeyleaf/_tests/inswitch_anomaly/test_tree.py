# -*- coding: utf-8 -*-

import logging
from typing import (
    List
)
import pytest

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

__version__ = "1.0"

import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.inswitch_anomaly import tree
from fengkeyleaf.logging import my_logging


# content of test_class.py
class TestClass:
    @pytest.mark.skip
    def test_one( self ):
        l: logging.Logger = my_logging.get_logger( logging.DEBUG )
        l.debug( "test" )
        x = "this"
        assert "h" in x

    @pytest.mark.skip
    def test_two( self ):
        x = "hello"
        assert hasattr( x, "check" )


# pytest -n auto -s -q test_tree.py
# https://docs.pytest.org/en/7.1.x/how-to/logging.html?highlight=log
class Tester:
    IS_WRITING: bool = True
    LOGGING_LEVEL: int = logging.DEBUG

    h1: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/UNSW_2018_IoT_Botnet_Dataset_Feature_Names.csv"
    h3: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/NUSW-NB15_features_name.csv"
    H_FULL: List[ str | None ] = [ None, None, None ]

    # Feature name list
    F_S: List[ str ] = [ fkl_inswitch.SRC_COUNT_STR, fkl_inswitch.SRC_TLS_STR, fkl_inswitch.DST_COUNT_STR, fkl_inswitch.DST_TLS_STR ]
    F_S_O: List[ str ] = [ fkl_inswitch.RANGE_STR ]

    dt1_o: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches"
    dt2_o: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/sketches"
    dt3_o: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/sketches"
    V_FULL_O: List[ str ] = [ dt1_o, dt2_o, dt3_o ]

    dt1: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches_new"
    dt2: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/sketches_new"
    dt3: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/sketches_new"
    V_FULL: List[ str ] = [ dt1, dt2, dt3 ]

    # Validation with wanted features and unlimited sketch
    @pytest.mark.skip
    def test_bot_lot_wanted_unlimited_sketch( self ) -> None:
        dt: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches_new"
        V: List[ str ] = [ "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/sketches_new" ]
        H: List[ str | None ] = [ None ]

        # Tree( None, dt, V, True, 10 ).train( None, H, _Tester.F_S )
        # Tree( None, _Tester.dt1_o, _Tester.V_FULL_O, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S_O )
        tree.Tree( None, Tester.dt1, Tester.V_FULL, Tester.IS_WRITING, Tester.LOGGING_LEVEL ).train( None, Tester.H_FULL, Tester.F_S )
        # tree.Tree( None, Tester.dt1, [ Tester.dt1 ], Tester.IS_WRITING, 10 ).train( None, [ None ], Tester.F_S )

    @pytest.mark.skip
    def test_ton_lot_wanted_unlimited_sketch( self ) -> None:
        # Tree( None, _Tester.dt2_o, _Tester.V_FULL_O, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S_O )
        tree.Tree( None, Tester.dt2, Tester.V_FULL, Tester.IS_WRITING, Tester.LOGGING_LEVEL ).train( None, Tester.H_FULL, Tester.F_S )

    @pytest.mark.skip
    def test_unsw_nb15_wanted_unlimited_sketch( self ) -> None:
        # Tree( None, _Tester.dt3_o, _Tester.V_FULL_O, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S_O )
        tree.Tree( None, Tester.dt3, Tester.V_FULL, Tester.IS_WRITING, Tester.LOGGING_LEVEL ).train( None, Tester.H_FULL, Tester.F_S )

    # Validation sets to test without balancing.
    dt1_limited: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/BoT-IoT/original/re-formatted"
    dt2_limited: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/202 p 3 spring/NetworkingResearch/data/TON_IoT/Processed_Network_dataset/original/re-formatted"
    dt3_limited: str = "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/original/re-formatted"
    V_FULL_limited: List[ str ] = [
        dt1_limited, dt2_limited, dt3_limited
    ]
    IS_LIMITED_SKETCH: bool = True
    OPTIMIZATION_STRATEGY: int = fkl_inswitch.LINEAR_OP

    # Validation with wanted features and limited sketch
    # @pytest.mark.skip
    def test_bot_lot_wanted_limited_sketch( self ) -> None:
        # Training is unlimited, but validation is limited.
        tree.Tree(
            None,
            Tester.dt1,
            [ Tester.dt1_limited ],
            Tester.IS_WRITING,
            Tester.LOGGING_LEVEL
        ).train(
            None,
            [ None ],
            Tester.F_S,
            {
                fkl_inswitch.IS_SKETCHING_STR: True,
                fkl_inswitch.IS_OPTIMIZING_STR: False,
                fkl_inswitch.LIMITATION_STR: 4
            }
        )

    @pytest.mark.skip
    def test_ton_lot_wanted_limited_sketch( self ) -> None:
        tree.Tree( None, Tester.dt1, [ Tester.dt2_limited ], Tester.IS_WRITING, Tester.LOGGING_LEVEL ).train( None, [ None ], Tester.F_S, Tester.IS_LIMITED_SKETCH )
        # Tree( None, _Tester.dt2, _Tester.V_FULL_limited, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S, _Tester.SKETCH_LIMITATION )

    @pytest.mark.skip
    def test_unsw_nb15_wanted_limited_sketch( self ) -> None:
        tree.Tree( None, Tester.dt1, [ Tester.dt3_limited ], Tester.IS_WRITING, Tester.LOGGING_LEVEL ).train( None, [ None ], Tester.F_S, Tester.IS_LIMITED_SKETCH )
        # Tree( None, _Tester.dt3, _Tester.V_FULL_limited, _Tester.IS_WRITING, 10 ).train( None, _Tester.H_FULL, _Tester.F_S, _Tester.SKETCH_LIMITATION )

