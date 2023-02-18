#include "./sketch.p4"

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress( 
    inout headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata 
) {
    Sketch() s;

    action drop() {
        mark_to_drop( standard_metadata );
    }

    action ipv4_forward( macAddr_t dstAddr, egressSpec_t port ) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table decision_tree {
        key = {
            meta.src_count_select: range;
            meta.src_tls_select: range;
            meta.dst_count_select: range;
            meta.dst_tls_select: range;
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
        s.apply( hdr, meta, standard_metadata );

        decision_tree.apply();
    }
}