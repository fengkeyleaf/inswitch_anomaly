/***************** M A T C H - A C T I O N  *********************/

control Egress( 
    /* User */
    inout my_egress_headers_t                          hdr,
    inout my_egress_metadata_t                         meta,
    /* Intrinsic */
    in    egress_intrinsic_metadata_t                  eg_intr_md,
    in    egress_intrinsic_metadata_from_parser_t      eg_prsr_md,
    inout egress_intrinsic_metadata_for_deparser_t     eg_dprsr_md,
    inout egress_intrinsic_metadata_for_output_port_t  eg_oport_md ) 
{
    action drop() {
        eg_dprsr_md.drop_ctl = 1;
    }

    apply {
        // Prune multicast packet to ingress port to preventing loop
        // if ( standard_metadata.egress_port == standard_metadata.ingress_port )
        //     drop();
    }
}
