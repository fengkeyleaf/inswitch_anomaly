# -*- coding: utf-8 -*-
"""
file to do sketch building and write results to a csv file

sean bergen
"""

import csv
import sys
import random as rd

import pandas
from pandas import (
    DataFrame
)

"""
functions to update the sketch
"""


# lowest count, the simplest one
def lowest_count( IP, sketch ):
    in_sketch = False
    for i in range( len( sketch ) ):
        if IP in sketch[ i ]:
            sketch[ i ][ 1 ] = sketch[ i ][ 1 ] + 1
            in_sketch = True
            # reset tls
            sketch[ i ][ 2 ] = 0
    # if ip was not in sketch, find smallest count to
    # replace
    if in_sketch == False:
        min_n = sketch[ 0 ][ 1 ]
        min_i = 0
        for i in range( len( sketch ) ):
            # replace empty indices
            if sketch[ i ][ 1 ] == None:
                min_i = i
                break
            # we also check if there are any we haven't
            # seen in a long time and replace them over
            # low counts
            if sketch[ i ][ 2 ] == 0:
                min_i = i
                min_n = -1
            # if no empty indices go find small
            # count among vals
            if sketch[ i ][ 1 ] < min_n:
                min_n = sketch[ i ][ 1 ]
                min_i = i
        sketch[ min_i ] = [ IP, 1, 0 ]
    # increment all other TLS
    for i in range( len( sketch ) ):
        if sketch[ i ][ 2 ] == None:
            pass
        else:
            sketch[ i ][ 2 ] = sketch[ i ][ 2 ] + 1


# highest tls, the second-simplest one
def highest_tls( IP, sketch ):
    in_sketch = False
    for i in range( len( sketch ) ):
        if IP in sketch[ i ]:
            sketch[ i ][ 1 ] = sketch[ i ][ 1 ] + 1
            in_sketch = True
            # reset tls
            sketch[ i ][ 2 ] = 0
    # if ip was not in sketch, find largest tls to (time last seen)
    # replace
    if in_sketch == False:
        min_n = sketch[ 0 ][ 2 ]
        min_i = 0
        for i in range( len( sketch ) ):
            # replace empty indices
            if sketch[ i ][ 2 ] == None:
                min_i = i
                break
            # if no empty indices go find large
            # tls among vals
            if sketch[ i ][ 2 ] > min_n:
                min_n = sketch[ i ][ 2 ]
                min_i = i
        sketch[ min_i ] = [ IP, 1, 0 ]
    # increment all other TLS
    for i in range( len( sketch ) ):
        if sketch[ i ][ 2 ] == None:
            pass
        else:
            sketch[ i ][ 2 ] = sketch[ i ][ 2 ] + 1


# don't replace, the third-simplest one (replace if empty)
def no_replace( IP, sketch ):
    in_sketch = False
    for i in range( len( sketch ) ):
        if IP in sketch[ i ]:
            sketch[ i ][ 1 ] = sketch[ i ][ 1 ] + 1
            # reset tls
            sketch[ i ][ 2 ] = 0
            in_sketch = True
    if in_sketch == False:
        for i in range( len( sketch ) ):
            # replace empty indices
            if sketch[ i ][ 1 ] == None:
                sketch[ i ] = [ IP, 1, 0 ]
                break
    # increment all other TLS
    for i in range( len( sketch ) ):
        if sketch[ i ][ 2 ] == None:
            pass
        else:
            sketch[ i ][ 2 ] = sketch[ i ][ 2 ] + 1


# replace indice with the lowest value for count mult with ttl
def low_score( IP, sketch ):
    in_sketch = False
    for i in range( len( sketch ) ):
        if IP in sketch[ i ]:
            sketch[ i ][ 1 ] = sketch[ i ][ 1 ] + 1
            in_sketch = True
            # reset tls
            sketch[ i ][ 2 ] = 0
    # if ip was not in sketch, find smallest count to
    # replace
    if in_sketch == False:
        if sketch[ i ][ 1 ] == None:
            min_n = 0
        else:
            min_n = sketch[ 0 ][ 1 ] * (1000 - sketch[ 0 ][ 2 ])
        min_i = 0
        for i in range( len( sketch ) ):
            # replace empty indices
            if sketch[ i ][ 1 ] == None:
                min_i = i
                break
            # if no empty indices go find small
            # count among vals
            if sketch[ i ][ 1 ] * sketch[ i ][ 2 ] < min_n:
                min_n = sketch[ i ][ 1 ] * sketch[ i ][ 2 ]
                min_i = i
        sketch[ min_i ] = [ IP, 1, 0 ]
    # increment all other TLS
    for i in range( len( sketch ) ):
        if sketch[ i ][ 2 ] == None:
            pass
        else:
            sketch[ i ][ 2 ] = sketch[ i ][ 2 ] + 1


# sketch is size 2 list containing sources sketch and dest sketch
#
# row is the current packet we are looking at, [1] = src.ip, [2] = dst.ip
#
# r is a random integer between [0,3] (both inclusive) and determines
# the policy we update the sketch with
def update_sketch( sketch, row, r ):
    if r == 0:
        lowest_count( row[ 1 ], sketch[ 0 ] )
        lowest_count( row[ 2 ], sketch[ 1 ] )
    if r == 1:
        highest_tls( row[ 1 ], sketch[ 0 ] )
        highest_tls( row[ 2 ], sketch[ 1 ] )
    if r == 2:
        no_replace( row[ 1 ], sketch[ 0 ] )
        no_replace( row[ 2 ], sketch[ 1 ] )
    if r == 3:
        low_score( row[ 1 ], sketch[ 0 ] )
        low_score( row[ 2 ], sketch[ 1 ] )


"""
read in label data
"""
file = open( sys.argv[ 1 ] )
reader = csv.reader( file )
# TODO: use pandas
f: DataFrame = pandas.read_csv( sys.argv[ 1 ] )

"""
build the sketch
"""
data = [ ]
labels = [ ]

header = next( reader )
# counter to reset the sketch every 1000 packets
counter = 0
sketch = [ [ [ None, None, None ] ] * 8, [ [ None, None, None ] ] * 8 ]
for row in reader:
    # reset the sketch every 1000 packets
    if counter % 100 == 0:
        # just to see
        print( sketch )
        # sketch = [[[None,None,None]]*8,[[None,None,None]]*8]
    counter = counter + 1

    # assuming we have labled data as our file

    # current policies:
    #    lowest_count
    #    lowest_ttl
    #    no_replace
    #    low_score
    r = rd.randrange( 4 )

    # we pass the data into the tree classifier as follows:
    #       0,1000 if not in sketch, ct,tls if in
    tmp = [ ]
    ind = -1
    for i in range( len( sketch[ 0 ] ) ):
        if row[ 1 ] == sketch[ 0 ][ i ][ 0 ]:
            ind = i
    if ind >= 0:
        tmp = [ sketch[ 0 ][ ind ][ 1 ], sketch[ 0 ][ ind ][ 2 ] ]
        # tmp = [sketch[0][ind][1],sketch[0][ind][2]]
    else:
        tmp = [ 0, 1000 ]
        # tmp = [0,1000]
    ind = -1
    for i in range( len( sketch[ 1 ] ) ):
        if row[ 2 ] == sketch[ 1 ][ i ][ 0 ]:
            ind = i
    if ind >= 0:
        tmp.append( sketch[ 1 ][ ind ][ 1 ] )
        tmp.append( sketch[ 1 ][ ind ][ 2 ] )
    else:
        tmp.append( 0 )
        tmp.append( 1000 )
    # update sketch afterwards
    update_sketch( sketch, row, r )

    data.append( list( tmp ) )

    labels.append( row[ len( row ) - 3 ] )

"""
write the sketches with labels to a file
"""

output = open( sys.argv[ 2 ], "w", newline = "" )
writer = csv.writer( output )

for i in range( len( data ) ):
    temp = [ ]
    temp.append( data[ i ] )
    temp.append( labels[ i ] )
    writer.writerow( temp )
