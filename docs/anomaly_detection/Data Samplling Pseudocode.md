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

