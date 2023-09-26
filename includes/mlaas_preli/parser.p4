/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser( packet_in pkt,
                 out headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata ) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract( hdr.ethernet );
        transition select( hdr.ethernet.etherType ) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        pkt.extract( hdr.ipv4 );
        transition parse_mlass;
    }

    state parse_mlass {
        pkt.extract( hdr.mlass );
        transition accept;
    }
}