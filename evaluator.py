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
        self.P: Dict[ float, Dict ] = None
        self.R: Dict[ str, str ] = None

    def __is_correct_good( self, k: float ) -> bool:
        """
        :param k: pkt ID number
        :return:
        """
        return self.P[ k ][ csvparaser.LABEL_STR ] == int( csvparaser.GOOD_LABEL_STR ) and str( k ) in self.R

    def __is_correct_bad( self, k: float ) -> bool:
        """
        :param k: pkt ID number
        :return:
        """
        return self.P[ k ][ csvparaser.LABEL_STR ] == int( csvparaser.BAD_LABEL_STR ) and not ( str( k ) in self.R )

    def __evaluate( self ) -> None:
        gc: int = 0 # good count
        bc: int = 0 # bad count
        gtc: int = 0 # good total count
        for k in self.P: # k: pkt ID number
            if self.P[ k ][ csvparaser.LABEL_STR ] == int( csvparaser.GOOD_LABEL_STR ):
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

        # https://java2blog.com/python-print-percentage-sign/
        print( "%d out of total %d pkts, accuracy = %.2f%%" % ( gc + bc, len( self.P ), ( ( gc + bc ) / len( self.P ) ) * 100 ) )
        print( "Correct gc = %d, bc = %d" % ( gc, bc ) )
        print( "Data set: %d out of %d are good pkts." % ( gtc, len( self.P ) ) )

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
    # Evaluator().evaluate( "./test/result.csv" )
    # Evalutor().evaluate( "./test/test_csv1_small.csv" )
    # Evaluator().evaluate( "/home/p4/tutorials/data/Bot-loT/UNSW_2018_IoT_Botnet_Dataset_2_reformatted.csv" )
    Evaluator().evaluate( "C:/Users/fengk/OneDrive/documents/computerScience/RIT/2023 spring/NetworkingResearch/data/UNSW-NB15-CSV/re-formatted-mapping/UNSW-NB15_1_reformatted.csv" )

