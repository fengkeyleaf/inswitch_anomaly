# 4/22 meeting summary

## 1. Problem

Currently, the date set is not balanced due to having too many bad pkts, and few good pkts, meaning that the decision tree only outputs bad pkts as result and thus can predicate very well. Also, to maintain the sketch as simple as possible for now, we need to keep the sketch as it is to only keep track src ip and st ip for now, and also not to track as many as features as possible due to the limitation of p4 language.

Consequently, we need to make the data set more balanced by using data sampling.

## 1. Solution - Data Sampling

In conclusion, we decided to use data sampling to balance the data set, here is the algorithm:

```java
Algorithm DATASAMPLING( D, p = 50% )
input. D is the list of all data set and expected probability p, where p is the ratio of ( expected number of good pkts / total number of pkts ).
output. List of balanced data set with the expected probability p.
s <- the sketch.
P <- empty list to store pkts.
gc <- 0 // good pkt count
tc <- 0 // total pkt count
for every data set, d, in D
     do for every pkt, p, in d
        tc++
        do update s with p as usual
            // make sure don't have too many bad pkts.
           if p is a good pkt
              then gc++
                   if gc / tc < p
                      then add p to P
                           gt++
           else if gc / tc > p
                then add p to P
return P
```

