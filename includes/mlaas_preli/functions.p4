bool assert_overflow( in int<32> a, in int<32> b, in int<32> c ) {
    // log_msg( "a={}, b={}, c={}", { a, b, c } );
    // a and b have different sign or
    return ( a >= 0 && b <= 0 ) || ( a <= 0 && b >= 0 ) ||
    // a and b have the same sign and c( = a + b ) must be the same sign as a's and b's.
     ( a >= 0 && b >= 0 && c >= 0 ) || ( a <= 0 && b <= 0 && c <= 0 );
}