#include "./workerCount.p4"
#include "./gradientUpdate.p4"

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control Ingress( 
    /* User */
    inout my_ingress_headers_t                       hdr,
    inout my_ingress_metadata_t                      meta,
    /* Intrinsic */
    in    ingress_intrinsic_metadata_t               ig_intr_md,
    in    ingress_intrinsic_metadata_from_parser_t   ig_prsr_md,
    inout ingress_intrinsic_metadata_for_deparser_t  ig_dprsr_md,
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md
) {
    // A Field variable must be initialized when it's used in a table key match,
    // Pool index converted(bit<15>) by mlaas.idx(bit<32>) 
    WorkerCount() worker_counter;
    GradientUpdate() grad_update;

    action send( PortId_t port ) {
        ig_tm_md.ucast_egress_port = port;
    }

    action drop() {
        ig_dprsr_md.drop_ctl = 1;
    }

    // bfrt_python
    // bfrt.mlaas_preli.pipe.Ingress
    // ipv4_lpm.add_with_send("10.0.1.1", 32, 1)
    // ipv4_lpm.add_with_send("10.0.2.2", 28, 2)
    table ipv4_lpm {
        key     = { hdr.ipv4.dstAddr : lpm; }
        actions = { send; drop; }

        default_action = drop;
    }

    apply {
        // Basic forwarding/routing.
        // With commenting out this block, 
        // the compiler will remove the table ipv4_lpm since it's useless.
        // if ( hdr.ipv4.isValid() ) {
        //     ipv4_lpm.apply();
        // }

        if ( hdr.ipv4.isValid() && hdr.mlaas.isValid() ) {
            worker_counter.apply( hdr, meta, ig_tm_md );
            grad_update.apply( hdr, meta, ig_tm_md );
        }
    }
}