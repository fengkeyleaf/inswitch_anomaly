// Cannot use GradientAddition and GradientSend
// error: Table placement cannot make any more progress.  
// Though some tables have not yet been placed, dependency analysis has found that no more tables are placeable.

control GradientSend(
    inout my_ingress_headers_t hdr,
    inout ingress_intrinsic_metadata_for_tm_t ig_tm_md,
    Register<bit<16>, pool_index_t> C,
    Register<unsigned_int32, pool_index_t> P_pos,
    Register<unsigned_int32, pool_index_t> P_neg,
    in pool_index_t idx
) {
    
    
    // TODO: define `multicast` action to multicast packets to group 1
    // Hint: Check v1model for multicast group
    // TODO: Asynchronous condition, pool idx may be incorrect.
    action multicast() {
        ig_tm_md.mcast_grp_a = 1;
    }

    // error: overlap. Both Register Ingress.P_pos and Ingress.C require the meter address hardware, and cannot be on the same table tbl_grad_send.
    action grad_send_pos_a() {
        P_pos.write( idx, 0 );
    }
    
    action grad_send_neg_a() {
        P_neg.write( idx, 0 );
    }

    action grad_send_post_a() {
        P_pos.write( idx, 0 );
        P_neg.write( idx, 0 );

        // C.write( idx, 0 );

        // Update pkt's sign is alwasy False, which is easy to verify.
        hdr.mlaas.sign = 0;

        // Send back updates to multicast group 1
        multicast();
    }

    table grad_send_t {
        key = {
            hdr.mlaas.numberOfWorker: exact;
        }
        actions = {
            grad_send_post_a;
            NoAction;
        }
        default_action = NoAction;
        const entries = {
            NUMBER_OF_WORKER : grad_send_post_a;
        }
        size = 1;
    }

    apply {
        grad_send_t.apply();
    }
}