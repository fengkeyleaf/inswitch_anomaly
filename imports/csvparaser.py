import pandas as pd
from typing import Dict

ID_STR = "No."
SRC_ADDR_STR = "Source"
SRC_MAC_STR = "SrcMac"
DST_ADDR_STR = "Destination"
DST_MAC_STR = "DstMac"

# https://stackoverflow.com/questions/11706215/how-can-i-fix-the-git-error-object-file-is-empty/12371337#12371337
def parse( f:str ) -> Dict[ str, Dict ]:
    """
    :param f: file path to the csv file.
    :return: { 
        pkt_id: {
            srcAddr: srcIP, dstAddr: dstIP,
            srcMac: srcMac, dstMac: dstMac
        }
    }
    """
    dic:Dict = {}
    id:int = 0
    # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    # https://pandas.pydata.org/docs/reference/frame.html
    # https://www.geeksforgeeks.org/python-next-method/
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.html?highlight=series#pandas.Series
    for r in pd.read_csv( f ).iterrows():
        s = r[ 1 ];
        assert dic.get( s[ ID_STR ] ) is None, "Already seen this ID before."
        id = id + 1
        if ( s[ ID_STR ] == 1 ):
            continue
        
        assert id == int( s[ ID_STR ] ) # Consistent incremental id garaunteed
        # print( "s=%s, d=%s" % ( s[ "Source" ], s[ "Destination" ] ) )
        dic[ s[ ID_STR ] ] = {
            SRC_ADDR_STR: s[ SRC_ADDR_STR ],
            DST_ADDR_STR: s[ DST_ADDR_STR ],
            SRC_MAC_STR: None,
            DST_MAC_STR: None
        }
    
    return dic


if __name__ == '__main__':
    print( parse( "../test/test_csv1_small.csv" ) )