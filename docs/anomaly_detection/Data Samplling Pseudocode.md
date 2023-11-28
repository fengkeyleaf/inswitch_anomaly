# Data Processing

```java
Algorithm MIX( O, M )
Input. Original data set, O, and made-up data set, M.
Output. Data Set, D, combining O and M sorted by pkt timestamps.
D <- Append M to O
Sort D by timestamp ( colmun ).
```

# Pkt Alignment

```java
Algorithm PKTALIGNMENT( o, m, rt = 0 )
Input. Aligned original data set, o, made-up data sets, m.
Output. Data set, d, combining o and M sorted by pkt timestamps, and relative pkt time, rt.
if m is already reltive to 0
   then Align m reltive to rt, i.e each pkt time += rt.
   	    rt = time of the last pkt of m.
d <- concat( o, m )
Sort d by pkt timestamps.
return ( d, rt )
```

# Data sampling

```java
Algorithm DATASAMPLING( P )
Input. P is input data set to generate a sketch csv file. Assuming we have labled data.
Output. Balanced sketch csv file to train a decision tree.
gdp <- gc / len( P ) // good Drop Percent
bdp <- bc / len( P ) // bad Drop Percent
s <- sketch without the limitation threshold.
D <- list of sketch data formatted as [ [ srcCount, srcTLS, dstCount, dstTLS ], label ]
for every pkt, p, in P
    Increment the TLS of every tracked ip in s.
    Record p's srcIP and p's dstIP in s.
    ifAddGood <- p is a good one and randDoube() > gdp
    ifAddBad <- p is a bad one and randDoube() > bdp
    if ifAddGood or ifAddBad
        then D <- [ [ srcCount in s, srcTL in s, dstCount in s, dstTLS in s ], label ]
return D
```

