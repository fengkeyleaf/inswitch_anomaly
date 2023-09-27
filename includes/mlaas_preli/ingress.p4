#include "./functions.p4"

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress( 
    inout headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata 
) {
    register<int32>( POOL_SIZE ) P;  // Gradient pool
    // Assume that worker count == grad count,
    // and increment grad count even if the worker doesn't provide the grad, 0 by default.
    register<bit<16>>( POOL_SIZE ) C;  // Worker Count

    // A Field variable must be initialized when it's used in a table key match,
    // Current cumulative gradient value.
    int32 r = 0;
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

    action grad_add() {
        // bit<32> is unsigned type, so no need to do: -1 < hdr.mlass.idx && 
        assert( hdr.mlass.idx < POOL_SIZE );
        log_msg( "idx={}", { hdr.mlass.idx } );

        P.read( r, hdr.mlass.idx );
        assert( assert_overflow( r, hdr.mlass.grad, r + hdr.mlass.grad ) );
        r = r + hdr.mlass.grad;
        P.write( hdr.mlass.idx, r );

        C.read( c, hdr.mlass.idx );
        c = c + 1;
        C.write( hdr.mlass.idx, c );
    }

    // TODO: How to ideal with a normal pkt?
    table gradient_addition_t {
        key = {
            hdr.mlass.idx: range;
        }
        actions = {
            grad_add;
            NoAction;
        }
        default_action = NoAction;
        const entries = {
            ( 0 .. 7 ) : grad_add;
        }
    }

    action grad_send() {
        hdr.mlass.grad = r;
        P.write( hdr.mlass.idx, 0 );
        hdr.mlass.numberOfWorker = c;
        C.write( hdr.mlass.idx, 0 );
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
        if ( hdr.ipv4.isValid() ) {
            ipv4_lpm.apply();
        }

    //     if ( hdr.ipv4.isValid() && hdr.mlass.isValid() ) {
    //         gradient_addition_t.apply();
    //         gradient_update_t.apply();
    //     }
    }
}