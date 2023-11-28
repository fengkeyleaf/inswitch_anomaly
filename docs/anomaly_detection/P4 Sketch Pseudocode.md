```java
// P4 Version
// Entry algorithm
Algorithm SKETCHCLASSIFICATION( p )
Input. Incomming packet.
Initialize the following global variables:
    c <- 0 // Global IP counter.
    I <- Array of size of 16, each element in it is bit<48> presenting macAddr_t.
    C <- Array of size of 16, each element in it is bit<10> presenting counts for ips.
    T <- Array of size of 16, each element in it is bit<10> presenting TLS for ips.
if p has a valid ipv4 header
   then SKETCH( p.header.ipv4.srcAddr )
        SKETCH( p.header.ipv4.dstAddr )
        Run the feature tables and then run the decision tree in the control plane.
        Increment every element in T by 1, as well as c.
        if c >= 1000
           then Reset every element in T to 0, as well as c.
   else Drop p.
       
Algorithm SKETCH( a )
Input. IP address, either srcAddr or dstAddr.
if ISREPLACE( a ) is true
   // Neither p's srcAddr nor p's dstAddr is in the Sketch.
   // Start the replacement policy.
   then rand <- get a random number from 0 to 3, inclusive.
        if rand == 0 // Replace lowest count
           then LOWESTCOUNT( a )
           else if rand == 1 // Highest TLS
                   then HIGHESTTLS( a )
           else if rand == 2 // smallest count and tls score, calculated by count * ( 1000 - tls )
                   then SMALLFESTTLS( a )
           // No replace when rand == 3

Algorithm ISREPLACE( a )
Input. IP address, either srcAddr or dstAddr.
Output. To tell if we need to apply the replace policy.
if I contains a, and locating at the index i
   then C[ i ] = C[ i ] + 1
        T[ i ] = 0
        return false
   else if HASEMPTY( a )
           then return false
           else return true

Algorithm HASEMPTY( a )
Input. IP address, either srcAddr or dstAddr.
Output. To tell if there is an empty spot.
i <- Find the index so that I[ index ] is empty ( So are C[ index ] and T[ index ] )
if such i exists:
   then REPLACE( i, a )
        return true
   else return false

Algorithm REPLACE( i, a )
Input. index where the replacement happens, and IP address to be replaced.
I[ i ] = a
C[ i ] = 1
T[ i ] = 0

Algorithm LOWESTCOUNT( a )
Input. IP address, either srcAddr or dstAddr.
i <- Find the index so that C[ index ] is the lowest in C.
REPLACE( i, a )

Algorithm HIGHESTTLS( a )
Input. IP address, either srcAddr or dstAddr.
i <- Find the index so that T[ index ] is the highest in T.
REPLACE( i, a )

Algorithm SMALLFESTTLS( a )
Input. IP address, either srcAddr or dstAddr.
i <- Find the index so that T[ index ] is the smallest in T.
REPLACE( i, a )
```



```java
// Python Version
// Global algorithm ( Data sampling )
Algorithm DATASAMPLING( P )
Input. P is input data set to generate a sketch csv file. Assuming we have labled data.
Output. Balanced sketch csv file to train a decision tree.
gdp <- gc / len( P ) // good Drop Percent
bdp <- bc / len( P ) // bad Drop Percent
s <- sketch without the limitation threshold.
Initialize the following global variables for the sketch s:	
	c <- 0 // Global IP counter.
    l <- 0 // non-positive, indicating that this sketch has limitation.
	S <- Array of size of n, each element in it is a dict[ src ip, its info ].
	D <- Array of size of n, each element in it is a dict[ dst ip, its info ].
SD <- list of sketch data formatted as [ [ srcCount, srcTLS, dstCount, dstTLS ], label ]
for every pkt, p, in P
    L = SKETCHCLASSIFICATION( p )
    ifAddGood <- p is a good one and randDoube() > gdp
    ifAddBad <- p is a bad one and randDoube() > bdp
    if ifAddGood or ifAddBad
        then SD <- [ *L, label ]
return SD

// Sketching algorithm
Algorithm SKETCHCLASSIFICATION( p )
Input. Incomming packet, p.
Output. List of feature values extracted from the sketch based on the packet, p.
// Record p's srcIP and p's dstIP in s.
ADD( S, p.header.ipv4.srcAddr )
ADD( D, p.header.ipv4.dstAddr )
Increment the TLS of every tracked ip in s.
if l > 0 and c >= 1000
    then Reset the TLS of every tracked ip to 0, as well as c.
return [ p's srcCount, p's srcTLS, p's dstCount, p's dstTLS ]
    
Algorithm ADD( dic, ip )
Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
if dic contains ip:
   then dic[ ip ][ IP_COUNT ] += 1
        dic[ ip ][ IP_TLS ] = 0
else REPLACE( dic, ip )
    
Algorithm REPLACE( dic, ip )
Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
if HASEMPTY( dic )
   then TREACK( dic, ip )
else r <- get a random number from 0 to 3, inclusive.
     if r == 0 // Replace lowest count
          then LOWESTCOUNT( dic, ip )
     else if r == 1 // Highest TLS
          then HIGHESTTLS( dic, ip )
     else if r == 2 // smallest count and tls score, calculated by count * ( 1000 - tls )
          then SMALLFESTTLS( dic, ip )
     // No replace when rand == 3

Algorithm HASEMPTY( dic )
Input. A dict, dic, to store a key-value pair, ( ip, ip's info ).
Output. To tell if the sketch has an empty spot or not.
// Either no limitation or the current number of elements in dic is less than the limitation.
return l <= 0 or len( dic ) < l
                                                
Algorithm TREACK( dic, ip )
Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
assert that ip is not in dic.
dic[ ip ][ IP_COUNT ] = 1
dic[ ip ][ IP_TLS ] = 0         
         
Algorithm LOWESTCOUNT( dic, ip )
Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
i <- Find the ip, i, so that dic[ i ][ IP_COUNT ] is the lowest in dic.
Remove the key-value pair with i as the key.
TREACK( dic, ip )

Algorithm HIGHESTTLS( dic, ip )
Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
i <- Find the ip, i, so that dic[ i ][ IP_TLS ] is the highest in dic.
Remove the key-value pair with i as the key.
TREACK( dic, ip )

Algorithm SMALLFESTTLS( dic, ip )
Input. A dict, dic, to store a key-value pair, ( ip, ip's info ), and an incoming ip.
i <- Find the ip, i, so that dic[ i ][ IP_TLS ] is the smallest in dic.
Remove the key-value pair with i as the key.
TREACK( dic, ip )
```

