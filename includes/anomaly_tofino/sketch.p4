
// https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4#L710
// TODO: Define the behavior when no replacement policy applied.
// TODO: Replacement policy: replace the last one when ties.
// TODO: all integers are 32-bit for consistency now. And then adjust them to better ones.
control Sketch( 
    /* User */
    inout my_ingress_headers_t      hdr,
    inout my_ingress_metadata_t     meta 
) {
    // 1. Initialize the following global variables:
    // https://p4.org/p4-spec/docs/P4-16-v1.2.2.html#sec-default-values
    int32 c = 0; // Global IP counter.
    int32 ik = -1; // Index for current pkt located in the Skecth.
    int32 iks = -1; // Index for srcAddr of current pkt located in the Skecth.
    int32 ikd = -1; // Index for dstAddr of current pkt located in the Skecth.

    // T specifies the type of each entry
    // I specifies the type of the index of an indirect register extern.
    // extern Register<T, I> {
        // Register(bit<32> size);
        // Register(bit<32> size, T initial_value);
    // }
    
    // control example<M>(M meta) {
        // Register<bit<32>, _>(4096) counters;
        // RegisterAction<_, _, void> increment_counter = {
            // void apply(inout bit<32> value) {
            // value = value + meta.increment_amount;
            // }
        // };
        // action trigger_counter() {
            // increment_counter.execute(meta.index);
        // }
    // }
    
    // Array of size of 16, each element in it is bit<48> presenting macAddr_t.
    Register<ip4Addr_t, _>( ARRAY_LEN ) I;
    // Array of size of 16, each element in it is bit<10> presenting counts for ips.
    Register<int32, _>( ARRAY_LEN ) C;
    // Array of size of 16, each element in it is bit<10> presenting TLS for ips.
    Register<int32, _>( ARRAY_LEN ) T;

    int32 scv = -1; // src count value
    int32 stv = -1; // src tls valule
    int32 dcv = -1; // dst count value
    int32 dtv = -1; // dst tls value

    /////////////////////////////////////

    // https://p4.org/p4-spec/docs/P4-16-v1.2.2.html#sec-invoke-actions
    action src_count_select_a( int32 v ) {
        meta.src_count_select = v;
    }

    table src_count_select_t {
        key = {
            scv: range;
        }

        actions = {
	        NoAction;
            src_count_select_a;
        }

        size = 1024;
    } 

    action src_tls_select_a( int32 v ) {
        meta.src_tls_select = v;
    }

    table src_tls_select_t {
        key = {
            stv: range;
        }

        actions = {
	        NoAction;
            src_tls_select_a;
        }

        size = 1024;
    } 

    action dst_count_select_a( int32 v ) {
        meta.dst_count_select = v;
    }

    table dst_count_select_t {
        key = {
            dcv: range;
        }

        actions = {
	        NoAction;
            dst_count_select_a;
        }

        size = 1024;
    } 

    action dst_tls_select_a( int32 v ) {
        meta.dst_tls_select = v;
    }

    table dst_tls_select_t {
        key = {
            dtv: range;
        }

        actions = {
	        NoAction;
            dst_tls_select_a;
        }

        size = 1024;
    } 

    /////////////////////////////////////

    bool is_empty = false;
    int32 ie = -1; // empty index

    action find_empty( int32 i ) {
        assert( i >= 0 && i < 16 );
        // read count for the ip locating at index i.
        int32 res = -1;
        C.read( res, ( bit<32> ) i );
        assert( res >= 0 );

        // Find empty place only for once.
        assert( res != 0 || ( res == 0 && ( ie == -1 || ie > -1 ) ) );
        // count(res) == 0 meaning no ip repace at i, emtpy space.
        // There may be several empty spots, use the first one.
        if ( res == 0 && ie == -1 ) {
            ie = i;
        }
    }

    // Algorithm REPLACE( i, a )
    // Input. index where the replacement happens, and IP address to be replaced.
    action replace( in int32 i, in ip4Addr_t a ) {
        // 1. I[ i ] = a
        I.write( ( bit<32> ) i, a );
        // 2. C[ i ] = 1
        C.write( ( bit<32> ) i, 1 );
        // 3. T[ i ] = 0
        T.write( ( bit<32> ) i, 0 );
    }

    // Algorithm HASEMPTY( a )
    // Input. IP address, either srcAddr or dstAddr.
    // Output. To tell if there is an empty spot.
    action has_empty( in ip4Addr_t a ) {
        // 1. i <- Find the index so that I[ index ] is empty ( So are C[ index ] and T[ index ] )
        // 2. if such i exists
        if ( ie > -1 ) {
            // 3. then ik = i
            ik = ie;
            // 4. REPLACE( i, a )
            // replace( ie, a );
            // 5. return true
            is_empty = true;
            return;
        }

        // 6. else return false
        is_empty = false;
    }

    bool is_replace = false;
    int32 ir = -1; // replace index

    action find_replace( int32 i, ip4Addr_t a ) {
        assert( i >= 0 && i < 16 );
        ip4Addr_t ip = 0;
        I.read( ip, ( bit<32> ) i );
        assert( ip >= 0 );

        assert( ip != a || ip == a && ir == -1 );
        if ( ip == a ) {
            ir = i;
        }
    }

    // Algorithm ISREPLACE( a )
    // Input. IP address, either srcAddr or dstAddr.
    // Output. To tell if we need to apply the replace policy.
    action is_replace_a( in ip4Addr_t a ) {
        // Found a spot to replace, no replacement or fill-in-empty happened before.
        assert( ir == -1 || ir > -1 && ik == -1 );
        // Found an empty spot to fill in, no replacement or fill-in-empty happened before.
        assert( ie == -1 || ie > -1 && ik == -1 );

        // 1. if I contains a, locating at the index i
        if ( ir > -1 ) {
            // 2. ik = i
            ik = ir;
            // https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4#L351
            // void write(in bit<32> index, in T value);
            // 3. then C[ i ] = C[ i ] + 1
            // int<32> v = -1;
            // C.read( v, ( bit<32> ) i );
            // C.write( ( bit<32> ) i, v + 1 );
            // 4, T[ i ] = 0
            // T.write( ( bit<32> ) i, 0 );
            // 5. return false
            is_replace = false;
            return;
        } 

        
        // 6. else if HASEMPTY( a )
        has_empty( a );
        if ( is_empty ) {
            // 7. then return false
            is_replace = false;
            return;
        }
        
        // 8. else return true
        is_replace = true;
    }

    int32 ilc = -1; // lowest count index
    int32 lc = MAX_COUNT;

    action find_lowest_count( int32 i, ip4Addr_t a ) {
        assert( i >= 0 && i < 16 );
        int32 ct = -1;
        C.read( ct, ( bit<32> ) i );
        assert( ct >= 0 );

        if ( ct < lc ) {
            ilc = i;
            ct = lc;
        }
    }

    // Algorithm LOWESTCOUNT( a )
    // Input. IP address, either srcAddr or dstAddr.
    action lowest_count( in ip4Addr_t a ) {    
        // 1. i <- Find the index so that C[ index ] is the lowest in C. 
        // find_lowest_count();

        // 2. REPLACE( i, a )
        assert( ilc > -1 );
        replace( ilc, a );
    }

    int32 iht = -1; // highest tls index
    int32 ht = -1; // highefst tls

    action find_highest_tls( int32 i ) {
        assert( i >= 0 && i < 16 );
        int32 tls = -1;
        T.read( tls, ( bit<32> ) i );
        assert( tls >= 0 );

        if ( tls > ht ) {
            iht = i;
            ht = tls;
        }
    }

    // Algorithm HIGHESTTLS( a )
    // Input. IP address, either srcAddr or dstAddr.
    action highest_tls( in ip4Addr_t a ) {
        // 1. i <- Find the index so that T[ index ] is the highest in T.
        // find_highest_tls();

        // 2. REPLACE( i, a )
        assert( iht > -1 );
        replace( iht, a );
    }

    int32 ist = -1; // smallest tls index
    int32 st = MAX_TLS; // smallest tls

    action find_smallest_tls( int32 i ) {
        assert( i >= 0 && i < 16 );
        int32 tls = -1;
        T.read( tls, ( bit<32> ) i );
        assert( tls >= 0 );
        int32 ct = -1;
        C.read( ct, ( bit<32> ) i );
        assert( ct >= 0 );

        int32 ctls = cal_smallest_tls( ct, tls );
        if ( ctls < st ) {
            ist = i;
            st = ctls;
        }
    }

    // Algorithm SMALLFESTTLS( a )
    // Input. IP address, either srcAddr or dstAddr.
    action smallest_tls( in ip4Addr_t a ) {
        // i <- Find the index so that T[ index ] is the smallest in T. // *
        // find_smallest_tls();

        // REPLACE( i, a )
        assert( ist > -1 );
        replace( ist, a );
    }

    int32 r = -1; 

    // Algorithm SKETCH( a )
    // Input. IP address, either srcAddr or dstAddr.
    action sketch( in ip4Addr_t a ) {
        assert( r == -1 );
        // Cannot call extern functions in conditional action block.
        // int32 r; // random number [0, 3].
        // https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4#L367
        // extern void random<T>(out T result, in T lo, in T hi);
        random( r, 0, 3 );
        // https://github.com/p4lang/p4c/blob/main/p4include/v1model.p4#L668
        // extern void assert(in bool check );
        assert( r >= 0 && r <= 3 );
        // log_msg( "r={}", { r } );

        // 1. if ISREPLACE( a ) is true
        is_replace_a( a );
        // Apply replacement policy when neither no empty spot nor a(addr) not in record.
        assert( !is_replace || ( ie == -1 && ir == -1 ) );
        if ( is_replace ) {
            // Neither p's srcAddr nor p's dstAddr is in the Sketch.
            // Start the replacement policy.
            // 2. then rand <- get a random number from 0 to 3, inclusive.
            // 3. if r == 0 // Replace lowest count
            if ( r == 0 ) {
                // 4. then LOWESTCOUNT( a )
                // lowest_count( a );
            }
            // 5. else if r == 1 // Highest TLS
            else if ( r == 1 ) {
                // 6. r HIGHESTTLS( a )
                // highest_tls( a );
            }
            // 7. else if r == 2 // smallest count and tls score, calculated by count * ( 1000 - tls )
            else if ( r == 2 ) {
                // 8. then SMALLFESTTLS( a )
                // smallest_tls( a );
            }
            // No replace when r == 3
        }
    }

    action increment_tls( in int32 i ) {
        assert( i >= 0 && i < 16 );
        int32 tls = -1;
        T.read( tls, ( bit<32> ) i );
        assert( tls >= 0 );
        T.write( ( bit<32> ) i, tls + 1 );
    }

    action increment() {
        increment_tls( 0 );
        increment_tls( 1 );
        increment_tls( 2 );
        increment_tls( 3 );
        increment_tls( 4 );
        increment_tls( 5 );
        increment_tls( 6 );
        increment_tls( 7 );
        increment_tls( 8 );
        increment_tls( 9 );
        increment_tls( 10 );
        increment_tls( 11 );
        increment_tls( 12 );
        increment_tls( 13 );
        increment_tls( 14 );
        increment_tls( 15 );

        c = c + 1;
    }

    action reset_tls( in int32 i ) {
        assert( i >= 0 && i < 16 );
        T.write( ( bit<32> ) i, 0 );
    }

    action reset() {
        reset_tls( 0 );
        reset_tls( 1 );
        reset_tls( 2 );
        reset_tls( 3 );
        reset_tls( 4 );
        reset_tls( 5 );
        reset_tls( 6 );
        reset_tls( 7 );
        reset_tls( 8 );
        reset_tls( 9 );
        reset_tls( 10 );
        reset_tls( 11 );
        reset_tls( 12 );
        reset_tls( 13 );
        reset_tls( 14 );
        reset_tls( 15 );

        c = 0;
    }

    // https://p4.org/p4-spec/docs/P4-16-v-1.2.3.html#sec-invoke-actions
    apply {

        // 2. if p has a valid ipv4 header
        if ( hdr.ipv4.isValid() ) {
            assert( hdr.ipv4.srcAddr != 0 );
            assert( hdr.ipv4.srcAddr != hdr.ipv4.dstAddr );

            // Reset indice.
            ik = -1;
            iks = -1;
            ikd = -1;
            
            // Look for ir for srcAddr, index from 0 ~ 7
            ir = -1;
            find_replace( 0, hdr.ipv4.srcAddr );
            find_replace( 1, hdr.ipv4.srcAddr );
            find_replace( 2, hdr.ipv4.srcAddr );
            find_replace( 3, hdr.ipv4.srcAddr );
            find_replace( 4, hdr.ipv4.srcAddr );
            find_replace( 5, hdr.ipv4.srcAddr );
            find_replace( 6, hdr.ipv4.srcAddr );
            find_replace( 7, hdr.ipv4.srcAddr );

            // Look for ie for srcAddr, index from 0 ~ 7
            // A table can only be called once, no more than one!
            ie = -1;
            find_empty( 0 );
            find_empty( 1 );
            find_empty( 2 );
            find_empty( 3 );
            find_empty( 4 );
            find_empty( 5 );
            find_empty( 6 );
            find_empty( 7 );

            // 3. then SKETCH( p.header.ipv4.srcAddr )
            r = -1;
            sketch( hdr.ipv4.srcAddr );
            // 4. iks = ik
            // Find the spot in the sketch or replacement policy applied.
            assert( ik > -1 || r > -1 );
            iks = ik;
            // Fill empty place process.
            // Increment process first, when srcAddr is already stored in I and I has empty spaces.
            if ( ir == -1 && ie > -1 ) {
                replace( ie, hdr.ipv4.srcAddr );
            }

            // Increment process.
            if ( ir > -1 ) {
                int<32> v = -1;
                C.read( v, ( bit<32> ) ir );
                C.write( ( bit<32> ) ir, v + 1 );
                T.write( ( bit<32> ) ir, 0 );
            }


            // Replace policy process.
            if ( r == 0 && is_replace ) {
                ilc = -1;
                lc = MAX_COUNT;

                // Find lowest count index for srcAddr.
                find_lowest_count( 0, hdr.ipv4.srcAddr );
                find_lowest_count( 1, hdr.ipv4.srcAddr );
                find_lowest_count( 2, hdr.ipv4.srcAddr );
                find_lowest_count( 3, hdr.ipv4.srcAddr );
                find_lowest_count( 4, hdr.ipv4.srcAddr );
                find_lowest_count( 5, hdr.ipv4.srcAddr );
                find_lowest_count( 6, hdr.ipv4.srcAddr );
                find_lowest_count( 7, hdr.ipv4.srcAddr );

                // Replace at the index, and this is guarantee to happen.
                iks = ilc;
                lowest_count( hdr.ipv4.srcAddr );
            }
            else if ( r == 1 && is_replace ) {
                iht = -1;
                ht = -1;

                // Find highefst tls index for srcAddr.
                find_highest_tls( 0 );
                find_highest_tls( 1 );
                find_highest_tls( 2 );
                find_highest_tls( 3 );
                find_highest_tls( 4 );
                find_highest_tls( 5 );
                find_highest_tls( 6 );
                find_highest_tls( 7 );

                // Replace at the index, and this is guarantee to happen.
                iks = iht;
                highest_tls( hdr.ipv4.srcAddr );
            }
            else if ( r == 2 && is_replace ) {
                ist = -1;
                st = MAX_TLS;

                // Find smallest tls index for srcAddr.
                find_smallest_tls( 0 );
                find_smallest_tls( 1 );
                find_smallest_tls( 2 );
                find_smallest_tls( 3 );
                find_smallest_tls( 4 );
                find_smallest_tls( 5 );
                find_smallest_tls( 6 );
                find_smallest_tls( 7 );

                // Replace at the index, and this is guarantee to happen.
                iks = ist;
                smallest_tls( hdr.ipv4.srcAddr );
            }

            // Either found a spot to replace or no replacement policy applied.
            assert( iks > -1 || r == 3 );

            /////////////////////////////////////
            // Don't forget to reset ik to -1, previous ik is recorded for srcAddr.
            ik = -1;
            // Look for ir for dstAddr, index from 8 ~ 15
            ir = -1;
            // find_replace( 3, hdr.ipv4.dstAddr );
            // find_replace( 4, hdr.ipv4.dstAddr );
            // find_replace( 5, hdr.ipv4.dstAddr );

            find_replace( 8, hdr.ipv4.dstAddr );
            find_replace( 9, hdr.ipv4.dstAddr );
            find_replace( 10, hdr.ipv4.dstAddr );
            find_replace( 11, hdr.ipv4.dstAddr );
            find_replace( 12, hdr.ipv4.dstAddr );
            find_replace( 13, hdr.ipv4.dstAddr );
            find_replace( 14, hdr.ipv4.dstAddr );
            find_replace( 15, hdr.ipv4.dstAddr );

            // Look for ie for dstAddr, index from 8 ~ 15
            ie = -1;
            // find_empty( 3 );
            // find_empty( 4 );
            // find_empty( 5 );

            find_empty( 8 );
            find_empty( 9 );
            find_empty( 10 );
            find_empty( 11 );
            find_empty( 12 );
            find_empty( 13 );
            find_empty( 14 );
            find_empty( 15 );

            // 5. SKETCH( p.header.ipv4.dstAddr )
            r = -1;
            sketch( hdr.ipv4.dstAddr );
            // 6. ikd = ik
            assert( ik > -1 || r > -1 );
            ikd = ik;
            // Fill empty place process.
            // Increment process first, when srcAddr is already stored in I and I has empty spaces.
            if ( ir == -1 && ie > -1 ) {
                replace( ie, hdr.ipv4.dstAddr );
            }

            // Increment process.
            if ( ir > -1 ) {
                // 2. then C[ i ] = C[ i ] + 1
                int<32> v = -1;
                C.read( v, ( bit<32> ) ir );
                C.write( ( bit<32> ) ir, v + 1 );
                // 3, T[ i ] = 0
                T.write( ( bit<32> ) ir, 0 );
            }

            // Replace policy process.
            if ( r == 0 && is_replace ) {
                ilc = -1;
                lc = MAX_COUNT;

                // Find lowest count index for dstAddr.
                // find_lowest_count( 3, hdr.ipv4.dstAddr );
                // find_lowest_count( 4, hdr.ipv4.dstAddr );
                // find_lowest_count( 5, hdr.ipv4.dstAddr );

                find_lowest_count( 8, hdr.ipv4.dstAddr );
                find_lowest_count( 9, hdr.ipv4.dstAddr );
                find_lowest_count( 10, hdr.ipv4.dstAddr );
                find_lowest_count( 11, hdr.ipv4.dstAddr );
                find_lowest_count( 12, hdr.ipv4.dstAddr );
                find_lowest_count( 13, hdr.ipv4.dstAddr );
                find_lowest_count( 14, hdr.ipv4.dstAddr );
                find_lowest_count( 15, hdr.ipv4.dstAddr );

                // Replace at the index, and this is guarantee to happen.
                ikd = ilc;
                lowest_count( hdr.ipv4.dstAddr );
            }
            else if ( r == 1 && is_replace ) {
                iht = -1;
                ht = -1;

                // Find highefst tls index for dstAddr.
                // find_highest_tls( 3 );
                // find_highest_tls( 4 );
                // find_highest_tls( 5 );

                find_highest_tls( 8 );
                find_highest_tls( 9 );
                find_highest_tls( 10 );
                find_highest_tls( 11 );
                find_highest_tls( 12 );
                find_highest_tls( 13 );
                find_highest_tls( 14 );
                find_highest_tls( 15 );

                // Replace at the index, and this is guarantee to happen.
                ikd = iht;
                highest_tls( hdr.ipv4.dstAddr );
            }
            else if ( r == 2 && is_replace ) {
                ist = -1;
                st = MAX_TLS;

                // Find smallest tls index for dstAddr.
                // find_smallest_tls( 3 );
                // find_smallest_tls( 4 );
                // find_smallest_tls( 5 );

                find_smallest_tls( 8 );
                find_smallest_tls( 9 );
                find_smallest_tls( 10 );
                find_smallest_tls( 11 );
                find_smallest_tls( 12 );
                find_smallest_tls( 13 );
                find_smallest_tls( 14 );
                find_smallest_tls( 15 );

                // Replace at the index, and this is guarantee to happen.
                ikd = ist;
                smallest_tls( hdr.ipv4.dstAddr );
            }

            assert( ikd > -1 || r == 3 );

            /////////////////////////////////////

            // 7. Run the feature tables and then run the decision tree in the control plane.
            // For now, iks and ikd may be -1 when no replacement policy applied.
            if ( iks > -1 ) {
                assert( iks >= 0 && iks < 16 );
                C.read( scv, ( bit<32> ) iks );
                log_msg( "scv={}", { scv } );
                src_count_select_t.apply();
                T.read( stv, ( bit<32> ) iks );
                log_msg( "stv={}", { stv } );
                src_tls_select_t.apply();
            }
            
            if ( ikd > -1 ) {
                assert( ikd >= 0 && ikd < 16 );
                C.read( dcv, ( bit<32> ) ikd );
                log_msg( "dcv={}", { dcv } );
                dst_count_select_t.apply();
                T.read( dtv, ( bit<32> ) ikd );
                dst_tls_select_t.apply();
            }

            // 8. Increment every element in T by 1, as well as c.
            increment();
            // 9. if c >= 1000
            if ( c >= 1000 ) {
                // 10. then Reset every element in T to 0, as well as c.
                reset();
            }
        }
    }
}