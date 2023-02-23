import pandas as pd
import argparse

# Refernce material: 
# https://github.com/p4lang/tutorials


def send( s, d ):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument( "-i", required=True, help="Path too input pkt file" )
    args = parser.parse_args();

    # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    D = pd.read_csv( args.i )
    # https://pandas.pydata.org/docs/reference/frame.html
    # https://www.geeksforgeeks.org/python-next-method/
    iter = D.iterrows();
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.html?highlight=series#pandas.Series
    # print( type( next( iter )[ 1 ] ) )
    # print( next( iter )[ 1 ].loc[ "Source" ] )
    i = 0
    for r in iter:
        s = r[ 1 ];
        print( "s=%s, d=%s" % ( s[ "Source" ], s[ "Destination" ] ) )
        i = i + 1 
        if ( i > 1 ):
            break
        send( s[ "Source" ], s[ "Destination" ] )
        