bool assert_overflow( in int32 a, in in32 b, in int32 c ) {
    // a and b have different sign or
    return ( a >= 0 && b <= 0 ) || ( a <= 0 && b >= 0 ) ||
    // a and b have the same sign and c( = a + b ) must be the same sign as a's and b's.
     ( a >= 0 && b >= 0 && c >= 0 ) || ( a <= 0 && b <= 0 && c <= 0 );
}