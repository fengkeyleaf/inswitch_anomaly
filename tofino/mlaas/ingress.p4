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
    // Assume that worker count == grad count,
    // and increment grad count even if the worker doesn't provide the grad, 0 by default.
    Register<bit<16>, _>( POOL_SIZE ) C; // Worker Count
    RegisterAction<bit<16>, _, bit<16>>( reg = C ) increment_worker_r = {
        void apply( inout bit<16> v, out bit<16> rv ) {
            v = v + 1;
            rv = v;
        }
    };
    RegisterAction<bit<16>, _, bit<16>>( reg = C ) reset_worker_r = {
        void apply( inout bit<16> v, out bit<16> rv ) {
            v = 0;
            rv = v;
        }
    };

    // Note that register doesn't support signed integers.
    Register<unsigned_int32, _>( POOL_SIZE ) P_pos; // Positive gradient pool
    RegisterAction<unsigned_int32, _, unsigned_int32>( reg = P_pos ) add_pos_r = {
        void apply( inout unsigned_int32 v, out unsigned_int32 rv ) {
            v = v + hdr.mlass.gradPos;
            rv = v;

            if ( C.read( hdr.mlass.idx ) == NUMBER_OF_WORKER ) {
                hdr.mlass.gradPos = v;
                v = 0;
                rv = v;

                // Update pkt's sign is alwasy False, which is easy to verify.
                hdr.mlass.sign = 0;
            }
        }
    };
    Register<unsigned_int32, _>( POOL_SIZE ) P_neg; // Negative gradient pool
    RegisterAction<unsigned_int32, _, unsigned_int32>( reg = P_neg ) add_neg_r = {
        void apply( inout unsigned_int32 v, out unsigned_int32 rv ) {
            v = v + hdr.mlass.gradNeg;
            rv = v;

            if ( C.read( hdr.mlass.idx ) == NUMBER_OF_WORKER ) {
                hdr.mlass.gradNeg = v;
                v = 0;
                rv = v;
                // Update pkt's sign is alwasy False, which is easy to verify.
                hdr.mlass.sign = 0;
            }
        }
    };

    // A Field variable must be initialized when it's used in a table key match,
    // Current count for the current param.
    bit<16> c = 0;

    action drop() {
        ig_dprsr_md.drop_ctl = 1;
    }

    action ipv4_forward( macAddr_t dstAddr, egressSpec_t port ) {
        // ig_tm_md.ucast_egress_port = port;
        ig_tm_md.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action grad_add_pos_a() {
        add_pos_r.execute( hdr.mlass.idx );
    }

    action grad_add_neg_a() {
        add_neg_r.execute( hdr.mlass.idx );
    }

    // TODO: How to ideal with a normal pkt?
    table gradient_addition_t {
        key = {
            hdr.mlass.idx: range;
            hdr.mlass.sign: exact;
        }
        actions = {
            grad_add_pos_a;
            grad_add_neg_a;
            NoAction;
        }
        default_action = NoAction;
        const entries = {
            ( 0 .. POOL_SIZE - 1, 0 ) : grad_add_pos_a;
            ( 0 .. POOL_SIZE - 1, 1 ) : grad_add_neg_a;
        }
    }

    // TODO: define `multicast` action to multicast packets to group 1
    // Hint: Check v1model for multicast group
    // TODO: Asynchronous condition, pool idx may be incorrect.
    action multicast() {
        ig_tm_md.mcast_grp = 1;
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
            increment_worker_r.execute( hdr.mlass.idx );

            if ( C.read( hdr.mlass.idx ) == NUMBER_OF_WORKER ) {
                reset_worker_r.execute( hdr.mlass.idx );
                multicast();
            }
        }
    }
}