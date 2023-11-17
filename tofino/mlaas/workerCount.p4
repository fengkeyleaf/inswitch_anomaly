control WorkerCount( 
    /* User */
    inout my_ingress_headers_t                       hdr,
    inout my_ingress_metadata_t                      meta,
    /* Intrinsic */
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md
) {
    pool_index_t idx = 0;
    Register<bit<16>, pool_index_t>( POOL_SIZE, 0 ) C; // Worker count
    RegisterAction<bit<16>, pool_index_t, bit<16>>( reg = C ) update_count = {
        void apply( inout bit<16> v, out bit<16> rv ) {
            if ( meta.is_reset ) {
                v = 1;
            }
            else {
                v = v + 1;
            }

            rv = v;
        }
    };

    action increment_worker_a() {
        hdr.mlaas.numberOfWorker = 0;
        if ( !meta.is_reset ) {
            C.read( idx );
        }
        hdr.mlaas.numberOfWorker = hdr.mlaas.numberOfWorker + 1;
        // hdr.mlaas.numberOfWorker == the one assigned by C.read( idx ),
        // not hdr.mlaas.numberOfWorker + 1
        C.write( idx, hdr.mlaas.numberOfWorker + 1 );

        // Equivalent:
        // hdr.mlaas.numberOfWorker = C.read( idx );
        // C.write( idx, hdr.mlaas.numberOfWorker + 1 );
        // hdr.mlaas.numberOfWorker = hdr.mlaas.numberOfWorker + 1;
    }

    action multicast_a() {
        ig_tm_md.mcast_grp_a = 1;
    }

    apply {
        idx = ( bit<15> ) hdr.mlaas.idx;

        hdr.mlaas.numberOfWorker = update_count.execute( idx );

        if ( hdr.mlaas.numberOfWorker == NUMBER_OF_WORKER ) {
            meta.is_reset = true;
            multicast_a();
        }
    }
}