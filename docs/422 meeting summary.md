# 4/22 meeting summary

## 1. Problem

Currently, the date set is not balanced due to having too many bad pkts, and few good pkts, meaning that the decision tree only outputs bad pkts as result and thus can predicate very well. Also, to maintain the sketch as simple as possible for now, we need to keep the sketch as it is to only keep track src ip and st ip for now, and also not to track as many as features as possible due to the limitation of p4 language.

Consequently, we need to make the data set more balanced by using data sampling.

## 1. Solution - Data Sampling

In conclusion, we decided to use data sampling to balance the data set, here is the algorithm:

```java
// Version 1
Algorithm DATASAMPLING( P )
input. P is input data set to generate a sketch csv file.
output. Balanced sketch csv file to train a decision tree.
s <- sketch without the limitation threshold.
gc <- 0 // good pkt count
bc <- 0 // bad pkt count
D <- list of sketch data formatted as [ [ srcCount, srcTLS, dstCount, dstTLS ], label ]
for every pkt, p, in P
    do if p is good one
          then gc++
       else bc++
       Increment the TLS of every tracked ip in s.
       Record srcIP and dstIP in s. If they are already in s, increment their count by 1. Otherwise, set their count and TSL to 1000. // Sean's stuff starts the TLS for an unseen pkt as very high, typicall 1000 in the current implementation.
       if random_doulbe() >= gc / bc
          then d <- [ 
           			  [ srcCount in s, srcTL in s, dstCount in s, dstTLS in s ],
                       label
       			   ]
           	   Append d to D.
return D
```

```java
// Version 2
Algorithm DATASAMPLING( P )
Input. P is input data set to generate a sketch csv file.
Output. Balanced sketch csv file to train a decision tree.
gc <- 0 // good pkt count
bc <- 0 // bad pkt count
for every pkt, p, in P
    do if p is a good one
          then gc++
       else bc++
gdp <- gc / len( P ) // good Drop Percent
bdp <- bc / len( P ) // bad Drop Percent
s <- sketch without the limitation threshold.
D <- list of sketch data formatted as [ [ srcCount, srcTLS, dstCount, dstTLS ], label ]
for every pkt, p, in P
    Increment the TLS of every tracked ip in s.
    Record p's srcIP and p's dstIP in s. If they are in s, increment its count by 1, otherwise set its count = 1 and TLS = 0.
    ifAddGood <- p is a good one and randDoube() > gdp
    ifAddBad <- p is a good one and randDoube() > bdp
    if ifAddGood or ifAddBad
         then d <- [ 
           			  [ srcCount in s, srcTL in s, dstCount in s, dstTLS in s ],
                       label
       			   ]
return D
```





















