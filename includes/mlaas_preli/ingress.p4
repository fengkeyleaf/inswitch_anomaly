#include "./functions.p4"

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress( 
    inout headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata 
) {
    // Note that register doesn't support signed integers.
    register<unsigned_int32>( POOL_SIZE ) P_pos;  // Positive gradient pool
    register<unsigned_int32>( POOL_SIZE ) P_neg; // Negative gradient pool
    // Assume that worker count == grad count,
    // and increment grad count even if the worker doesn't provide the grad, 0 by default.
    register<bit<16>>( POOL_SIZE ) C;  // Worker Count

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
            ( 0 .. 7, 0 ) : grad_add_pos;
            ( 0 .. 7, 1 ) : grad_add_neg;
        }
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

        // TODO: Boardcast the update.
        ipv4_forward( hdr.ethernet.srcAddr, standard_metadata.ingress_port );
    }

    table gradient_update_t {
        key = {
            c: exact;
        }
        actions = {
            grad_send;
            NoAction;
        }
        default_action = NoAction;
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