###
# Add to input csv to add dest MAC and src MAC
#   MACs are consistent with IPs
# Riley McGinn

import csv
import sys
import os
import math


# TODO: Functionality has been moved to pkt_processor.py
def spoof_MACs( csv_path: str ):
    temp_path = os.path.join( os.getcwd(), 'temp.csv' )
    input = open( csv_path )
    temp = open( temp_path, "w", newline = "" )
    reader = csv.reader( input )
    writer = csv.writer( temp )

    # Create a set of IPs in the csv
    ipset = set()

    # Iterate over the reader, adding IPs to the set
    next( reader )  # skip over header
    for packet in reader:
        ipset.add( packet[ 2 ] )
        ipset.add( packet[ 3 ] )

    # Create a dict to map IPs to MACs
    ipToMAC = { }

    # Iterate through ipset and add to dict
    # IP = key, MAC = value
    i = 0
    for ip in ipset:
        ipToMAC[ ip ] = create_MAC( i )
        i = i + 1

    # reset reader and re-iterate, adding MACs
    input.seek( 0 )
    reader = csv.reader( input )

    headers = next( reader )
    headers.append( "srcMAC" )
    headers.append( "dstMAC" )
    writer.writerow( headers )

    for packet in reader:
        packet.append( ipToMAC[ packet[ 2 ] ] )
        packet.append( ipToMAC[ packet[ 3 ] ] )
        writer.writerow( packet )

    # copy from temp to output
    temp.close()
    temp = open( temp_path )  # reopen in read mode
    reader = csv.reader( temp )
    input.close()
    output = open( csv_path, "w", newline = "" )  # repoen in write mode
    writer = csv.writer( output )
    for packet in reader:
        writer.writerow( packet )

    # file cleanup
    temp.close()
    os.remove( temp_path )
    output.close()


def create_MAC( input: int ):
    return \
            "{:02d}".format( math.trunc( ( input / 10000000000 ) ) % 100 ) + ':' + \
            "{:02d}".format( math.trunc( ( input / 100000000 ) ) % 100 ) + ':' + \
            "{:02d}".format( math.trunc( ( input / 1000000 ) ) % 100 ) + ':' + \
            "{:02d}".format( math.trunc( ( input / 10000 ) ) % 100 ) + ':' + \
            "{:02d}".format( math.trunc( ( input / 100 ) % 100 ) ) + ':' + \
            "{:02d}".format( input % 100 )


if __name__ == '__main__':
    spoof_MACs( sys.argv[ 1 ] )
