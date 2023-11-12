# -*- coding: utf-8 -*-

import logging
import re
from typing import Dict, Any, Tuple

import sklearn

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf.ml.metrics import f1_score
from fengkeyleaf.logging import my_logging
from fengkeyleaf.inswitch_anomaly import topo, filter
from fengkeyleaf import my_typing

__version__ = "1.0"

RESULT_STR: str = "result"
RESULT_INFO_STR: str = "result_info"
F1_STR: str = "F1_info"
SKLEARN_F1_STR: str = "sklearn_f1_info"
RESULT_FILE = "./output.json" # result file path


# TODO: Calculate F1 score.
class Evaluator:
    def __init__( self, is_forwarding: bool = False, ll: int = logging.INFO ) -> None:
        """

        @param is_forwarding: Evaluating mode where the switch only forwards a pkt without a decision tree.
        """
        self.l: logging.Logger = my_logging.get_logger( ll )

        self.P: Dict[ int, Dict[ str, str ] ] = None
        self.R: Dict[ str, Any ] = None
        self.is_forwarding: bool = is_forwarding

        self.f1: f1_score.F1Score = None

    # True - bad pkt, false - good pkt.
    # True positives
    def _count_tp( self, k: int ) -> None:
        """
        :param k: pkt ID number
        :return:
        """
        if ( self.P[ k ][ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.BAD_LABEL_STR ) and
                str( k ) not in self.R[ RESULT_STR ] ):
            self.f1.add_tp()

    # False positives
    def _count_fp( self, k: int ) -> None:
        if ( self.P[ k ][ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.GOOD_LABEL_STR ) and
                str( k ) not in self.R[ RESULT_STR ] ):
            self.f1.add_fp()

    # Ture negatives
    def _count_tn( self, k: int ) -> None:
        """
        :param k: pkt ID number
        :return:
        """
        if ( self.P[ k ][ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.GOOD_LABEL_STR ) and
                 ( str( k ) in self.R[ RESULT_STR ] ) ):
            self.f1.add_tn()

    # False negatives
    def _count_fn( self, k: int ) -> None:
        if ( self.P[ k ][ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.BAD_LABEL_STR ) and
                ( str( k ) in self.R[ RESULT_STR ] ) ):
            self.f1.add_fn()

    def __is_correct_forwarding( self, k: int ) -> bool:
        """
        :param k: pkt ID number
        :return:
        """
        return self.is_forwarding and self.__is_valid_pkt( k )

    def __is_valid_pkt( self, k: int ) -> bool:
        """
        :param k: pkt ID number
        :return:
        """
        return re.match( filter.IPV4_REG, self.P[ k ][ fkl_inswitch.DST_ADDR_STR ] ) is not None

    def __evaluate( self ) -> None:
        self.f1 = f1_score.F1Score()

        gtc: int = 0 # good total count
        rc: int = 0 # received pkt count
        rtc: int = 0 # received pkt total count
        for k in self.P: # k: pkt ID number
            if int( self.P[ k ][ fkl_inswitch.LABEL_STR ] ) == int( fkl_inswitch.GOOD_LABEL_STR ):
                gtc += 1

            assert my_typing.is_same_key( self.R[ RESULT_STR ], str( k ) )

            # https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
            self._count_tp( k )
            self._count_tn( k )
            self._count_fp( k )
            self._count_fn( k )

            self.f1.add_y(
                int( self.P[ k ][ fkl_inswitch.LABEL_STR ] ),
                1 if self.R[ RESULT_STR ].get( str( k ) ) is None else 0
            )

            if self.__is_correct_forwarding( k ): rc += 1;
            if self.__is_valid_pkt( k ): rtc += 1;

        self._info( gtc, rc, rtc )

    def _info( self, gtc: int, rc: int, rtc: int ) -> None:
        if self.is_forwarding:
            self.l.info( "%d out of total %d pkts, accuracy = %.2f%%" % ( rc, rtc, ( rc / rtc ) * 100 ) )
        else:
            assert len( self.P ) == self.f1.get_total()
            # https://java2blog.com/python-print-percentage-sign/
            s: str = "%d out of total %d pkts, accuracy = %.2f%%" % ( self.f1.get_trues(), len( self.P ), ( self.f1.get_trues() / len( self.P ) ) * 100 )
            self.l.info( s )
            self.R[ RESULT_INFO_STR ] = s
            s = "Correct gc = %d, bc = %d" % ( self.f1.get_tp(), self.f1.get_tn() )
            self.l.info( s )
            self.R[ RESULT_INFO_STR ] += " | " + s
            s = "Data set: %d out of %d are good pkts." % ( gtc, len( self.P ) )
            self.l.info( s )
            self.R[ RESULT_INFO_STR ] += " | " + s

            self.f1.cal()
            s = "acc=%.4f, pre=%.4f, re=%.4f, f1=%.4f" % ( self.f1.acc, self.f1.pre, self.f1.re, self.f1.f1 )
            self.R[ F1_STR ] = s
            s = " | tp=%d, fp=%d, tn=%d, fn=%d" % ( self.f1.get_tp(), self.f1.get_fp(), self.f1.get_tn(), self.f1.get_fn() )
            self.R[ F1_STR ] += s

            ( y_true, y_pre ) = self.f1.get_y()
            # accuracy_score
            r: float = sklearn.metrics.accuracy_score( y_true, y_pre )
            # precision_recall_fscore
            # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_fscore_support.html#sklearn-metrics-precision-recall-fscore-support
            R: Tuple[ float, float, float, None ] = sklearn.metrics.precision_recall_fscore_support(
                y_true, y_pre,
                average = "binary"
            )
            # confusion_matrix
            # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html#sklearn-metrics-confusion-matrix
            # tn, fp, fn, tp
            M: Tuple[ float, float, float, float ] = sklearn.metrics.confusion_matrix(
                y_true, y_pre
            ).ravel()
            self.R[ SKLEARN_F1_STR ] = str( [ r, *R ] + [ *M ] )

    def evaluate( self, f: str, dic: Dict[ str, Any ] ) -> None:
        """
        :param f: Output json file
        :return:
        """
        self.P = topo.Parser().parse( f )
        self.R = dic
        self.__evaluate()


