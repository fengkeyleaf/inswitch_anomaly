/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress( inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata ) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    apply {
        // Prune multicast packet to ingress port to preventing loop
        // if ( standard_metadata.egress_port == standard_metadata.ingress_port )
        //     drop();
    }
}
