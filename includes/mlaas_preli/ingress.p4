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
    register<int32>( POOL_SIZE ) C;  // Worker Count

    // Current count for the current param.
    bit<16> c;
    // Current cumulative gradient value.
    int32 r;

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
        assert( -1 < hdr.mlass.idx && hdr.idx < POOL_SIZE );
        log_msg( "idx={}, ie={}, ik={}", { hdr.mlass.idx } );

        P.read( r, hrd.mlass.idx );
        assert( assert_overflow( r, hdr.mlass.grad, r + hdr.mlass.grad ) );
        r = r + hdr.mlass.grad;
        P.write( hrd.mlass.idx, r );

        C.read( c, hrd.mlass.idx );
        c = c + 1;
        C.write( hrd,.mlass.idx, c );
    }

    // TODO: How to ideal with a normal pkt?
    table gradient_addition_t {
        key = {
            hdr.mlass.idx: exact;
        }
        actions = {
            grad_add;
            ipv4_forward;
        }
        size = 1024;
        default_action = ipv4_forward;
    }

    action grad_send() {
        hdr.mlass.grad = r;
        P.write( hrd.mlass.idx, 0 );
        hdr.mlass.number_of_worker = c;
        C.write( hrd,.mlass.idx, 0 );
        send( hdr.ipv4.dstAddr, standard_metadata.ingress_port );
    }

    table gradient_update_t {
        key = {
            c: extract
        }
        actions = {
            grad_send;
            NoAction;
        }
        size = 1024;
        const entries = {
            ( NUMBER_OF_WORKER ): grad_send;
            _: NoAction
        }
    }

    apply {
        if ( hdr.ipv4.isValid() && hdr.mlass.isValid() ) {
            gradient_addition_t.apply();
            gradient_update_t.apply();
        }
    }
}