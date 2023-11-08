#include "./sketch.p4"

/*************************************************************************
 **************  I N G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

/* **********************  H E A D E R S  *********************** */
struct my_ingress_headers_t {
    ethernet_h   ethernet;
    p4calc_h     p4calc;
}

/* *****  G L O B A L   I N G R E S S   M E T A D A T A  ******** */
struct my_ingress_metadata_t {
    int32 src_count_select;
    int32 src_tls_select;
    int32 dst_count_select;
    int32 dst_tls_select;
}

/* **********************  P A R S E R  ************************* */
parser IngressParser( 
    packet_in        pkt,
    /* User */
    out my_ingress_headers_t          hdr,
    out my_ingress_metadata_t         meta,
    /* Intrinsic */
    out ingress_intrinsic_metadata_t  ig_intr_md ) {

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
        transition accept;
    }

    state parse_tcp {
        pkt.extract( hdr.tcp );
        transition accept;
    }

}

/* **************** M A T C H - A C T I O N  ******************** */
control Ingress(
    /* User */
    inout my_ingress_headers_t                       hdr,
    inout my_ingress_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_t               ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md ) {

    Sketch() s;

    action drop() {
        ig_dprsr_md.drop_ctl = 1;
    }

    action ipv4_forward( macAddr_t dstAddr, PortId_t port ) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl |-| 1;
    }

    // Decsion by the decision tree.
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

	    const default_action = drop();
        size = 1024;
        
    }

    // Testing purpose: basic ipv4 forwarding.
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        
        const default_action = drop();
        size = 1024;
    }

    apply {
        // Basic forwarding/routing.
        // if ( hdr.ipv4.isValid() ) {
            // ipv4_lpm.apply();
        // }

        // Classification based on decision tree.
        // Apply the sketch first.
        s.apply( hdr, meta, standard_metadata );
        // Apply the tree with the info from the sketch.
        decision_tree.apply();
    }
}

/* ********************  D E P A R S E R  *********************** */
control IngressDeparser(
    packet_out                                       pkt,
    /* User */
    inout my_ingress_headers_t                       hdr,
    in    my_ingress_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md ) {

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