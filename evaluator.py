from typing import Dict

"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

from fengkeyleaf import (
    my_json,
    csvparaser
)
import receive as rec

RESULT_FILE = "./output.json" # result file path


class Evaluator:
    def __init__( self ) -> None:
        self.P: Dict = None
        self.R: Dict = None
        pass

    def __is_correct( self, k:str ) -> bool:
        """
        :param k: pkt ID number
        :return:
        """
        return (
            self.P[ k ][ csvparaser.LABEL_STR ] == int( csvparaser.GOOD_LABEL_STR ) and k in self.R
              ) or (
            self.P[ k ][ csvparaser.LABEL_STR ] == int( csvparaser.BAD_LABEL_STR ) and not ( k in self.R )
              )

    def __evaluate( self ) -> None:
        c: int = 0
        ct: int = 0
        for k in self.P: # k: pkt ID number
            if self.P[ k ][ csvparaser.LABEL_STR ] == int( csvparaser.GOOD_LABEL_STR ):
                ct += 1
            # https://www.geeksforgeeks.org/python-check-whether-given-key-already-exists-in-a-dictionary/
            if self.__is_correct( k ):
                c += 1

        # https://java2blog.com/python-print-percentage-sign/
        print( "%d out of total %d pkts, accuracy = %.2f%%" % ( c, len( self.P ), ( c / len( self.P ) ) * 100 ) )
        print( "Data set: %d out of %d are good pkts." % ( ct, len( self.P ) ) )

    def evaluate( self, f: str ) -> None:
        """
        :param f: Output json file
        :return:
        """
        self.P = csvparaser.Parser().parse( f )
        self.R = my_json.load( RESULT_FILE )[ rec.RESULT_STR ]
        self.__evaluate()


if __name__ == '__main__':
    # Evaluator().evaluate( "./test/result.csv" )
    # Evalutor().evaluate( "./test/test_csv1_small.csv" )
    Evaluator().evaluate( "/home/p4/tutorials/data/Bot-loT/UNSW_2018_IoT_Botnet_Dataset_2_reformatted.csv" )

