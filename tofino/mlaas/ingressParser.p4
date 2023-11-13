/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

/***********************  H E A D E R S  ************************/

struct my_ingress_headers_t {
    ethernet_h   ethernet;
    ipv4_h       ipv4;
    mlaas_h      mlaas;
}

/******  G L O B A L   I N G R E S S   M E T A D A T A  *********/

struct my_ingress_metadata_t {
    // int32 res;
}

parser IngressParser( packet_in pkt,
    /* User */
    out my_ingress_headers_t          hdr,
    out my_ingress_metadata_t         meta,
    /* Intrinsic */
    out ingress_intrinsic_metadata_t  ig_intr_md ) 
{
    Checksum() ipv4_checksum;

    /* This is a mandatory state, required by Tofino Architecture */
     state start {
        pkt.extract( ig_intr_md );
        pkt.advance( PORT_METADATA_SIZE );
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract( hdr.ethernet );
        //log_msg( "etherType={}", { hdr.ethernet.etherType } );
        transition select( hdr.ethernet.etherType ) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        pkt.extract( hdr.ipv4 );
        ipv4_checksum.add( hdr.ipv4 );
        //log_msg( "ipv4.dstAddr={}", { hdr.ipv4.dstAddr } );
        transition parse_mlaas;
    }

    state parse_mlaas {
        pkt.extract( hdr.mlaas );
        transition accept;
    }
}