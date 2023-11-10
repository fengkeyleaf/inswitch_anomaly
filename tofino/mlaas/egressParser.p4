/*************************************************************************
 ****************  E G R E S S   P R O C E S S I N G   *******************
 *************************************************************************/

/***********************  H E A D E R S  ************************/

struct my_egress_headers_t {
}

/********  G L O B A L   E G R E S S   M E T A D A T A  *********/

struct my_egress_metadata_t {
}

/***********************  P A R S E R  **************************/

parser EgressParser(
    packet_in        pkt,
    /* User */
    out my_egress_headers_t          hdr,
    out my_egress_metadata_t         meta,
    /* Intrinsic */
    out egress_intrinsic_metadata_t  eg_intr_md )
{
    /* This is a mandatory state, required by Tofino Architecture */
    state start {
        pkt.extract( eg_intr_md );
        transition accept;
    }
}
