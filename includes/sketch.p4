// https://p4.org/p4-spec/docs/P4-16-v1.2.2.html#sec-invoke-actions
// https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4#L710

// TODO: all integers are 32-bit for consistency now. And then adjust them to better ones.
control Sketch( 
    inout headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata 
) {
    // 1. Initialize the following global variables:
    // https://p4.org/p4-spec/docs/P4-16-v1.2.2.html#sec-default-values
    int32 c = 0; // Global IP counter.

    // https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4#L290
    // extern register<T> register(bit<32> size);

    // Array of size of 16, each element in it is bit<48> presenting macAddr_t.
    register<ip4Addr_t>( 16 ) I;
    // Array of size of 16, each element in it is bit<10> presenting counts for ips.
    register<int32>( 16 ) C;
    // Array of size of 16, each element in it is bit<10> presenting TLS for ips.
    register<int32>( 16 ) T;

    action drop() {
        mark_to_drop( standard_metadata );
    }

    action test( int32 i ) {
        log_msg( "i={}", { i } );
    }

    table test_t {
        key = {
            // meta.i: exact;
        }

        actions = {
            test;
        }

        // https://p4.org/p4-spec/docs/P4-16-v1.2.2.html#sec-entries
        // const entries = {
        //     _: test( 0 );
        //     1: test( 1 );
        //     2: test( 2 );
        // }
        default_action = test( 0 );
    }

    int32 iep = -1; // empty index parameter
    bool is_empty = false;
    // TODO: Set this in the apply block.
    int32 ie = -1; // empty index

    action find_empty_a( int32 i ) {
        assert( i >= 0 && i < 16 );
        int32 res = -1;
        C.read( res, ( bit<32> ) i );
        assert( res >= 0 );

        assert( res == 0 && ie == -1 );
        if ( res == 0 ) {
            ie = i;
        }
    }

    table find_empty_src_t {
        key = {
            iep: exact;
        }

        actions = {
            find_empty_a;
        }

        const entries = {
            0: find_empty_a( 0 );
            1: find_empty_a( 1 );
            2: find_empty_a( 2 );
            3: find_empty_a( 3 );
            4: find_empty_a( 4 );
            5: find_empty_a( 5 );
            6: find_empty_a( 6 );
            7: find_empty_a( 7 );
            // _: find_empty_a( -1 );
        }
    }

    // table find_empty_dst_t {
    //     key = {
    //         iep: exact;
    //     }

    //     actions = {
    //         find_empty_a;
    //     }

    //     const entries = {
    //         8: find_empty_a( 8 );
    //         9: find_empty_a( 9 );
    //         10: find_empty_a( 10 );
    //         11: find_empty_a( 11 );
    //         12: find_empty_a( 12 );
    //         13: find_empty_a( 13 );
    //         14: find_empty_a( 14 );
    //         15: find_empty_a( 15 );
    //     }
    // }

    // Algorithm REPLACE( i, a )
    // Input. index where the replacement happens, and IP address to be replaced.
    action replace( in int32 i, in ip4Addr_t a ) {
        // I[ i ] = a
        I.write( ( bit<32> ) i, a );
        // C[ i ] = 1
        C.write( ( bit<32> ) i, 1 );
        // T[ i ] = 0
        T.write( ( bit<32> ) i, 0 );
    }

    // Algorithm HASEMPTY( a )
    // Input. IP address, either srcAddr or dstAddr.
    // Output. To tell if there is an empty spot.
    action has_empty( in ip4Addr_t a ) {
        // 1. i <- Find the index so that I[ index ] is empty ( So are C[ index ] and T[ index ] )
        // 2. if such i exists
        if ( ie > -1 ) {
            // 3. REPLACE( i, a )
            // TODO: Move this into apply block.
            // replace( ie, a );
            // 4. return true
            is_empty = true;
            return;
        }

        // 5. else return false
        is_empty = false;
    }

    bool is_replace = false;
    // TODO: Set this in the apply block.
    int32 ir = -1; // replace index

    // Algorithm ISREPLACE( a )
    // Input. IP address, either srcAddr or dstAddr.
    // Output. To tell if we need to apply the replace policy.
    action is_replace_a( in ip4Addr_t a ) {
        // 1. if I contains a, locating at the index i
        if ( ir >= -1 ) {
            // https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4#L351
            // void write(in bit<32> index, in T value);
            // 2. then C[ i ] = C[ i ] + 1
            // int<32> v = -1;
            // C.read( v, ( bit<32> ) i );
            // C.write( ( bit<32> ) i, v + 1 );
            // 3, T[ i ] = 0
            // T.write( ( bit<32> ) i, 0 );
            // 4. return false
            is_replace = false;
            return;
        } 

        
        // 5. else if HASEMPTY( a )
        has_empty( a );
        if ( is_empty ) {
            // 6. then return false
            is_replace = false;
            return;
        }
        
        // 7. else return true
        is_replace = true;
    }

    action lowest_count() {

    }

    action highest_tls() {

    }

    action smallest_tls() {

    }

    // Algorithm SKETCH( a )
    // Input. IP address, either srcAddr or dstAddr.
    action sketch( in ip4Addr_t a ) {
        // Cannot call extern functions in conditional action block.
        int32 r; // random number [0, 3].
        // https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4#L367
        // extern void random<T>(out T result, in T lo, in T hi);
        random( r, 0, 3 );
        // https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4#L668
        // extern void assert(in bool check );
        assert( r >= 0 && r <= 3 );
        // log_msg( "r={}", { r } );

        // 1. if ISREPLACE( a ) is true
        ir = -1;
        is_replace_a( a );
        // is_replace = true;
        if ( is_replace ) {
            // Neither p's srcAddr nor p's dstAddr is in the Sketch.
            // Start the replacement policy.
            // 2. then rand <- get a random number from 0 to 3, inclusive.
            // 3. if r == 0 // Replace lowest count
            if ( r == 0 ) {
                // 4. then LOWESTCOUNT( a )
                lowest_count();
            }
            // 5. else if r == 1 // Highest TLS
            else if ( r == 1 ) {
                // 6. r HIGHESTTLS( a )
                highest_tls();
            }
            // 7. else if r == 2 // smallest count and tls score, calculated by count * ( 1000 - tls )
            else if ( r == 2 ) {
                // 8. then SMALLFESTTLS( a )
                smallest_tls();
            }
            // No replace when r == 3
        }
    }

    action increment() {

    }

    action reset() {

    }

    // https://p4.org/p4-spec/docs/P4-16-v-1.2.3.html#sec-invoke-actions
    apply {
        log_msg( "Sketch.p4" );
        // 2. if p has a valid ipv4 header
        if ( hdr.ipv4.isValid() ) {
            assert( hdr.ipv4.srcAddr != hdr.ipv4.dstAddr );
            // Look for ir.

            // Look for ie for srcAddr, index from 0 ~ 7
            // A table can only called once, no more than one!
            

            // 3. then SKETCH( p.header.ipv4.srcAddr )
            sketch( hdr.ipv4.srcAddr );
            if ( ir > -1 ) {
                // 2. then C[ i ] = C[ i ] + 1
                int<32> v = -1;
                C.read( v, ( bit<32> ) ir );
                C.write( ( bit<32> ) ir, v + 1 );
                // 3, T[ i ] = 0
                T.write( ( bit<32> ) ir, 0 );
            }

            // 4. SKETCH( p.header.ipv4.dstAddr )
            sketch( hdr.ipv4.dstAddr );
            // TODO: 5. Run the feature tables and then run the decision tree in the control plane.
            // 6. Increment every element in T by 1, as well as c.
            increment();
            // 7. if c >= 1000
            if ( c >= 1000 ) {
                // 8. then Reset every element in T to 0, as well as c.
                reset();
            }
        }

        // test_t.apply();
    }
}