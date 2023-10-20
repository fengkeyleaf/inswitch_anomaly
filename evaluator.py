import re
from typing import Dict
import logging

"""
file:
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

import fengkeyleaf.inswitch_anomaly as fkl_inswitch
from fengkeyleaf import (
    my_json,
    my_logging,
    csvparaser,
    filter
)
import receive as rec

RESULT_FILE = "./output.json" # result file path

# TODO: Integrate this into the receive.py
class Evaluator:
    def __init__( self, is_forwarding: bool = False, ll: int = logging.INFO ) -> None:
        """

        @param is_forwarding: Evaluating mode where the switch only forwards a pkt without a decision tree.
        """
        self.l: logging.Logger = my_logging.get_logger( ll )

        self.P: Dict[ float, Dict ] = None
        self.R: Dict[ str, str ] = None
        self.is_forwarding: bool = is_forwarding

    def __is_correct_good( self, k: float ) -> bool:
        """
        :param k: pkt ID number
        :return:
        """
        if self.P[ k ].get( fkl_inswitch.LABEL_STR ) is None: return False;

        return self.P[ k ][ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.GOOD_LABEL_STR ) and str( k ) in self.R

    def __is_correct_bad( self, k: float ) -> bool:
        """
        :param k: pkt ID number
        :return:
        """
        if self.P[ k ].get( fkl_inswitch.LABEL_STR ) is None: return False;

        return self.P[ k ][ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.BAD_LABEL_STR ) and not (str( k ) in self.R)

    def __is_correct_forwarding( self, k: float ) -> bool:
        """
        :param k: pkt ID number
        :return:
        """
        return self.is_forwarding and self.__is_valid_pkt( k )

    def __is_valid_pkt( self, k: float ) -> bool:
        """
        :param k: pkt ID number
        :return:
        """
        return re.match( filter.IPV4_REG, self.P[ k ][ fkl_inswitch.DST_ADDR_STR ] ) is not None

    def __evaluate( self ) -> None:
        gc: int = 0 # good count
        bc: int = 0 # bad count
        gtc: int = 0 # good total count
        rc: int = 0 # received pkt count
        rtc: int = 0 # received pkt total count
        for k in self.P: # k: pkt ID number
            if self.P[ k ][ fkl_inswitch.LABEL_STR ] == int( fkl_inswitch.GOOD_LABEL_STR ):
                gtc += 1
            # if k == 21:
            #     print( self.__is_correct( k ) )
                # print( self.P[ k ][ csvparaser.LABEL_STR ] == int( csvparaser.GOOD_LABEL_STR ) and k in self.R )
                # print( self.P[ k ][ csvparaser.LABEL_STR ] == int( csvparaser.BAD_LABEL_STR ) and not ( k in self.R ) )
                # print( k )
                # print( type( k ) )
                # print( ( k in self.R ) )
                # print( ( str( k ) in self.R ) )
                # print( not ( k in self.R ) )
            # https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
            if self.__is_correct_good( k ): gc += 1;
            if self.__is_correct_bad( k ): bc += 1;
            if self.__is_correct_forwarding( k ): rc += 1;
            if self.__is_valid_pkt( k ): rtc += 1;

        if self.is_forwarding:
            self.l.info( "%d out of total %d pkts, accuracy = %.2f%%" % ( rc, rtc, ( rc / rtc ) * 100 ) )
        else:
            # https://java2blog.com/python-print-percentage-sign/
            self.l.info( "%d out of total %d pkts, accuracy = %.2f%%" % ( gc + bc, len( self.P ), ( ( gc + bc ) / len( self.P ) ) * 100 ) )
            self.l.info( "Correct gc = %d, bc = %d" % ( gc, bc ) )
            self.l.info( "Data set: %d out of %d are good pkts." % ( gtc, len( self.P ) ) )

    def evaluate( self, f: str ) -> None:
        """
        :param f: Output json file
        :return:
        """
        self.P = csvparaser.Parser().parse( f )
        # self.R = my_json.load( RESULT_FILE )[ rec.RESULT_STR ]
        self.R = my_json.load( RESULT_FILE )[ rec.RESULT_STR ]
        self.__evaluate()


if __name__ == '__main__':
    # Initial Test
    # Evaluator().evaluate( "./test/result.csv" )
    # Evalutor().evaluate( "./test/test_csv1_small.csv" )

    # Real-world data Test
    # Evaluator().evaluate( "/home/p4/tutorials/data/Bot-loT/UNSW_2018_IoT_Botnet_Dataset_2_reformatted.csv" )
    # f: str = "/home/p4/tutorials/data/Bot-loT/dataSet/UNSW_2018_IoT_Botnet_Dataset_1_reformatted.csv"
    # f = "/home/p4/tutorials/data/UNSW-NB15/dataSet/UNSW-NB15_3_reformatted.csv"
    f = "/home/p4/BoT-loT/re-formatted/UNSW_2018_IoT_Botnet_Dataset_1_reformatted.csv"
    f = "/home/p4/data/UNSW_2018_IoT_Botnet_Dataset_1_reformatted.csv"
    Evaluator().evaluate( f )

    # Basic forwarding test
    f = "/home/p4/tutorials/data/swtich_test/Bot-loT_1.csv"
    # Evaluator( True ).evaluate( f )
