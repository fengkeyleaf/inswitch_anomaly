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
    bool is_reset;
    bool is_multicast;
    pool_index_t idx;
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
        transition select( hdr.ethernet.etherType ) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        pkt.extract( hdr.ipv4 );
        ipv4_checksum.add( hdr.ipv4 );
        transition parse_mlaas;
    }

    state parse_mlaas {
        pkt.extract( hdr.mlaas );
        // idx used to perform a range match cannot be bit<32> b/c
        // error: : Currently in p4c, the table gradient_addition_pos_t_0 cannot perform a range match on key 
        // ingress::hdr.mlaas.idx as the key does not fit in under 5 PHV nibbles
        meta.idx = ( pool_index_t ) hdr.mlaas.idx;
        transition accept;
    }
}