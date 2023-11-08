 /*********************  D E P A R S E R  ************************/

control IngressDeparser(
    packet_out pkt,
    /* User */
    inout my_ingress_headers_t                       hdr,
    in    my_ingress_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md ) 
{

    Checksum() ipv4_checksum;

    // TODO: Missing options
    apply {
        if ( hdr.ipv4.isValid() ) {
            hdr.ipv4.hdr_checksum = ipv4_checksum.update( {
                hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.diffserv,
                hdr.ipv4.total_len,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.frag_offset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.src_addr,
                hdr.ipv4.dst_addr
            } );
        }
        
        pkt.emit( hdr );
    }
}