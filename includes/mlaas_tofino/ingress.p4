#include "./functions.p4"

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control Ingress( 
    /* User */
    inout my_ingress_headers_t                       hdr,
    inout my_ingress_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_t               ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md
) {
    // Note that register doesn't support signed integers.
    Register<unsigned_int32, _>( POOL_SIZE ) P_pos; // Positive gradient pool
    RegisterAction<_, _, void>( reg = P_pos ) incre_p_pos = {
        void apply( inout unsigned_int32 v ) {
            v = v + 1;
        }
    }
    Register<unsigned_int32, _>( POOL_SIZE ) P_neg; // Negative gradient pool
    RegisterAction<_, _, void>( reg = P_neg ) incre_p_neg = {
        void apply( inout unsigned_int32 v ) {
            v = v + 1;
        }
    }
    // Assume that worker count == grad count,
    // and increment grad count even if the worker doesn't provide the grad, 0 by default.
    Register<bit<16>, _>( POOL_SIZE ) C; // Worker Count

    // A Field variable must be initialized when it's used in a table key match,
    // Current count for the current param.
    bit<16> c = 0;

    action drop() {
        mark_to_drop( standard_metadata );
    }

    action ipv4_forward( macAddr_t dstAddr, egressSpec_t port ) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action increment_worker() {
        C.read( c, hdr.mlass.idx );
        c = c + 1;
        C.write( hdr.mlass.idx, c );
    }

    action grad_add_pos() {
        log_msg( "max={}", { MAX_UNSIGNED_INT } );
        // bit<32> is unsigned type, so no need to do: -1 < hdr.mlass.idx && 
        assert( hdr.mlass.idx < POOL_SIZE );
        // log_msg( "idx={}", { hdr.mlass.idx } );

        unsigned_int32 r = 0;
        P_pos.read( r, hdr.mlass.idx );
        assert( MAX_UNSIGNED_INT - r >= hdr.mlass.gradPos );
        r = r + hdr.mlass.gradPos;
        // log_msg( "before: r={}", { r } );
        P_pos.write( hdr.mlass.idx, r );

        increment_worker();
    }

    action grad_add_neg() {
        // bit<32> is unsigned type, so no need to do: -1 < hdr.mlass.idx && 
        assert( hdr.mlass.idx < POOL_SIZE );
        // log_msg( "idx={}", { hdr.mlass.idx } );

        unsigned_int32 r = 0;
        P_neg.read( r, hdr.mlass.idx );
        assert( MAX_UNSIGNED_INT - r >= hdr.mlass.gradNeg );
        r = r + hdr.mlass.gradNeg;
        // log_msg( "before: r={}", { r } );
        P_neg.write( hdr.mlass.idx, r );

        increment_worker();
    }

    // TODO: How to ideal with a normal pkt?
    table gradient_addition_t {
        key = {
            hdr.mlass.idx: range;
            hdr.mlass.sign: exact;
        }
        actions = {
            grad_add_pos;
            grad_add_neg;
            NoAction;
        }
        default_action = NoAction;
        const entries = {
            ( 0 .. POOL_SIZE - 1, 0 ) : grad_add_pos;
            ( 0 .. POOL_SIZE - 1, 1 ) : grad_add_neg;
        }
    }

    // TODO: define `multicast` action to multicast packets to group 1
    // Hint: Check v1model for multicast group
    action multicast() {
        standard_metadata.mcast_grp = 1;
    }

    // TODO: Asynchronous condition, pool idx may be incorrect.
    action grad_send() {
        unsigned_int32 r = 0;
        P_pos.read( r, hdr.mlass.idx );
        hdr.mlass.gradPos = r;
        P_pos.write( hdr.mlass.idx, 0 );

        P_neg.read( r, hdr.mlass.idx );
        hdr.mlass.gradNeg = r;
        P_neg.write( hdr.mlass.idx, 0 );

        hdr.mlass.numberOfWorker = c;
        C.write( hdr.mlass.idx, 0 );

        // Update pkt's sign is alwasy False, which is easy to verify.
        hdr.mlass.sign = 0;

        assert( standard_metadata.ingress_port > 0 );
        // Send back to the ingress port
        // ipv4_forward( hdr.ethernet.srcAddr, standard_metadata.ingress_port );

        // Send back updates to port 2
        multicast();
    }

    table gradient_update_t {
        key = {
            c: exact;
        }
        actions = {
            grad_send;
            drop;
        }
        default_action = drop;
        const entries = {
            ( NUMBER_OF_WORKER ) : grad_send;
            // DefaultExpression invalid key expression
            // Maybe current complier doesn't support it.
            // _ : NoAction;
        }
    }

    // table_set_default MyIngress.ipv4_lpm MyIngress.drop
    // table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.1.1/32 => 08:00:00:00:01:11 1
    // table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.2.2/32 => 08:00:00:00:02:22 2
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    apply {
        // Basic forwarding/routing.
        // if ( hdr.ipv4.isValid() ) {
        //     ipv4_lpm.apply();
        // }

        if ( hdr.ipv4.isValid() && hdr.mlass.isValid() ) {
            gradient_addition_t.apply();
            gradient_update_t.apply();
        }
    }
}