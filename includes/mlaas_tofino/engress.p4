/***************** M A T C H - A C T I O N  *********************/

control Egress( 
    inout headers hdr,
    inout metadata meta,
    inout standard_metadata_t standard_metadata ) 
{
    action drop() {
        mark_to_drop(standard_metadata);
    }

    apply {
        // Prune multicast packet to ingress port to preventing loop
        // if ( standard_metadata.egress_port == standard_metadata.ingress_port )
        //     drop();
    }
}
