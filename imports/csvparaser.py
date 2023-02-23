import pandas as pd
import argparse

ID_STR = "No."
SRC_STR = "Source"
DST_STR = "Destination"

# https://stackoverflow.com/questions/11706215/how-can-i-fix-the-git-error-object-file-is-empty/12371337#12371337
def parse( f ):
    """
    :param f: file path to the csv file.
    :return: { ID: { srcAddr: srcIP, dstAddr: dstIP } }
    """
    dic = {}
    # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    # https://pandas.pydata.org/docs/reference/frame.html
    # https://www.geeksforgeeks.org/python-next-method/
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.html?highlight=series#pandas.Series
    for r in pd.read_csv( f ).iterrows():
        s = r[ 1 ];
        assert dic.get( s[ ID_STR ] ) is None, "Already seen this ID before."
        # print( "s=%s, d=%s" % ( s[ "Source" ], s[ "Destination" ] ) )
        dic[ s[ ID_STR ] ] = {
            SRC_STR: s[ SRC_STR ],
            DST_STR: s[ DST_STR ]
        }
    
    return dic

if __name__ == '__main__':
    print( parse( "../test/test_csv1_small.csv" ) )