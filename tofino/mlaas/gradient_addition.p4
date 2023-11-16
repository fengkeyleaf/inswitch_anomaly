// a parameter with type Register cannot have a direction
// in Register<bit<16>, pool_index_t> C

control GradientAddition(
    inout my_ingress_headers_t hdr,
    Register<bit<16>, pool_index_t> C,
    Register<unsigned_int32, pool_index_t> P_pos,
    Register<unsigned_int32, pool_index_t> P_neg,
    in pool_index_t idx
) {

    action increment_worker() {
        hdr.mlaas.numberOfWorker = C.read( idx );
        hdr.mlaas.numberOfWorker = hdr.mlaas.numberOfWorker + 1;
        // hdr.mlaas.numberOfWorker == the one assigned by C.read( idx ),
        // not hdr.mlaas.numberOfWorker + 1
        C.write( idx, hdr.mlaas.numberOfWorker + 1 );

        // Equivalent:
        // hdr.mlaas.numberOfWorker = C.read( idx );
        // C.write( idx, hdr.mlaas.numberOfWorker + 1 );
        // hdr.mlaas.numberOfWorker = hdr.mlaas.numberOfWorker + 1;
    }

    // Cannot combine gradient_addition_pos_t and gradient_addition_neg_t into one table, gradient_addition_t, b/c
    // error: table Ingress.gradient_addition_t: There are issues with the following indirect externs:
    // The action grad_add_pos_a uses Register Ingress.P_pos but does not use Register Ingress.P_neg.
    // The action grad_add_neg_a uses Register Ingress.P_neg but does not use Register Ingress.P_pos.
    // The Tofino architecture requires all indirect externs to be addressed with the same expression across all actions they are used in. 

    // Also, error: At most one stateful ALU operation with a given address is allowed per action. Writing to ingress::hdr.mlaas.gradNeg is not allowed here.
    // i.e. following code is not allowed.
    // hdr.mlaas.gradPos = P_pos.read( hdr.mlaas.idx );
    // P_pos.write( hdr.mlaas.idx, 0 );
    // hdr.mlaas.gradNeg = P_neg.read( hdr.mlaas.idx );
    // P_neg.write( hdr.mlaas.idx, 0 );

    action grad_add_pos_a() {
        // It seems that Register.read() and Reister.write() will be executed as a whole,
        // even if how many lines of code between them,
        // they're independent.
        unsigned_int32 r = P_pos.read( idx );
        P_pos.write( idx, r + hdr.mlaas.gradPos );
        hdr.mlaas.gradPos = r + hdr.mlaas.gradPos;

        // Incorrect:
        // We will not get cumlmative positive values.
        // Only the current hdr.mlaas.gradPos + previous hdr.mlaas.gradPos.
        // unsigned_int32 r = P_pos.read( idx );
        // hdr.mlaas.gradPos = r + hdr.mlaas.gradPos;
        // P_pos.write( idx, hdr.mlaas.gradPos );
    }

    // TODO: How to ideal with a normal pkt?
    table gradient_addition_pos_t {
        key = {
            idx: range;
            hdr.mlaas.sign: exact;
        }
        actions = {
            grad_add_pos_a;
            NoAction;
        }
        default_action = NoAction;
        const entries = {
            ( 0 .. ( pool_index_t ) POOL_SIZE - 1, 0 ) : grad_add_pos_a;
        }
        size = 1;
    }

    action grad_add_neg_a() {
        unsigned_int32 r = P_neg.read( idx );
        P_neg.write( idx, r + hdr.mlaas.gradNeg );
        hdr.mlaas.gradNeg = r + hdr.mlaas.gradNeg;
    }

    table gradient_addition_neg_t {
        key = {
            idx: range;
            hdr.mlaas.sign: exact;
        }
        actions = {
            grad_add_neg_a;
            NoAction;
        }
        default_action = NoAction;
        const entries = {
            ( 0 .. ( pool_index_t ) POOL_SIZE - 1, 1 ) : grad_add_neg_a;
        }
        size = 1;
    }
    
    apply {
        // Gradient aggregation
        gradient_addition_pos_t.apply(); // positive gradient
        gradient_addition_neg_t.apply(); // negative gr/adient
        increment_worker();
    }

}