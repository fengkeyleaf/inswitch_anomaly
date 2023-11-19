control GradientUpdate(
    /* User */
    inout my_ingress_headers_t                       hdr,
    inout my_ingress_metadata_t                      meta,
    /* Intrinsic */
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md
) {
    Register<int<32>, pool_index_t>( POOL_SIZE, 0 ) G; // Gradients
    RegisterAction<int<32>, pool_index_t, int<32>>( reg = G ) update_grad = {
        void apply( inout int<32> v, out int<32> rv ) {
            if ( meta.is_reset ) {
                v = hdr.mlaas.v;
            }
            else {
                v = v + hdr.mlaas.v;
            }

            rv = v;
        }
    };

    action multicast_a() {
        ig_tm_md.mcast_grp_a = 1;
    }

    apply {
        hdr.mlaas.v = update_grad.execute( meta.idx );

        if ( meta.is_multicast ) {
            multicast_a();
        }
    }
}