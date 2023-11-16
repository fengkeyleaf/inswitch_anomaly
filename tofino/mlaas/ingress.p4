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
    // The type argument I specifies the type of the index of an indirect register extern. 
    // This type can typically be inferred by the compiler.
    // The type argument T specifies the type of each entry, 
    // i.e. the type of state stored in each entry of the register.
    // extern Register<T, I> {
    //     Register(bit<32> size);
    //     Register(bit<32> size, T initial_value);
    // }
    // Register<int32, _>( 5, 0 ) calcultor;

    // Registers are accessed via RegisterAction externs, which contain a function named
    // apply that can read and update the value of one entry of a Register. Up to four
    // separate RegisterActions may be defined for a single Register extern, but only one
    // RegisterAction may be executed per packet for a given Register.

    // The apply method in a RegisterAction may be declared with either one or two arguments;
    // the first inout argument is the value of the Register entry being read and
    // updated, while the second optional out argument is the value 
    // that will be returned by the execute method when it is called in a table action.
    // R is the return value type.
    // extern RegisterAction<T, I, R> {
    //     Register( reg );
    // }
    // RegisterAction<int32, _, int32>( reg = calcultor )
    // calcuate = {
    //     void apply( inout int32 value, out int32 read_value ) {
    //         value = hdr.p4calc.op_a + hdr.p4calc.op_b;
    //         read_value = value;
    //     }
    // };

    // Each indirect extern has at least one method that can update one of its entries, 
    // e.g. execute(index) for a DirectMeter.

    // Uses of all registers within a single action have to use the same addressing.
    // i.e. both indices must be the same one.
    /// Return the value of register at specified index.
    // T read(in I index);

    /// Write value to register at specified index.
    // void write(in I index, in T value);

    // Assume that worker count == grad count,
    // and increment grad count even if the worker doesn't provide the grad, 0 by default.
    Register<bit<16>, pool_index_t>( POOL_SIZE, 0 ) C; // Worker Count
    // RegisterAction<bit<16>, _, bit<16>>( C ) increment_worker_r = {
    //     void apply( inout bit<16> v, out bit<16> rv ) {
    //         v = v + 1;
    //         rv = v;
    //     }
    // };
    // RegisterAction<bit<16>, _, bit<16>>( C ) reset_worker_r = {
    //     void apply( inout bit<16> v, out bit<16> rv ) {
    //         rv = v;
    //         v = 0;
    //     }
    // };

    // Note that register doesn't support signed integers.
    Register<unsigned_int32, pool_index_t>( POOL_SIZE, 0 ) P_pos; // Positive gradient pool
    // RegisterAction<unsigned_int32, _, unsigned_int32>( reg = P_pos ) add_pos_r = {
    //     void apply( inout unsigned_int32 v, out unsigned_int32 rv ) {
    //         v = v + hdr.mlaas.gradPos;
    //         rv = v;
    //     }
    // };
    // RegisterAction<unsigned_int32, _, unsigned_int32>( reg = P_pos ) reset_pos = {
    //     void apply( inout unsigned_int32 v, out unsigned_int32 rv ) {
    //         // Cannot assign pkt field here b/c
    //         // error: Can't assign to hdr.mlaas.gradPos in RegisterAction
    //         // hdr.mlaas.gradPos = v;
    //         rv = v;
    //         v = 0;
    //     }
    // };

    Register<unsigned_int32, pool_index_t>( POOL_SIZE, 0 ) P_neg; // Negative gradient pool
    // RegisterAction<unsigned_int32, _, unsigned_int32>( reg = P_neg ) add_neg_r = {
    //     void apply( inout unsigned_int32 v, out unsigned_int32 rv ) {
    //         v = v + hdr.mlaas.gradNeg;
    //         rv = v;
    //     }
    // };
    // RegisterAction<unsigned_int32, _, unsigned_int32>( reg = P_neg ) reset_neg = {
    //     void apply( inout unsigned_int32 v, out unsigned_int32 rv ) {
    //         rv = v;
    //         v = 0;
    //     }
    // };

    // A Field variable must be initialized when it's used in a table key match,
    // Pool index converted(bit<15>) by mlaas.idx(bit<32>) 
    pool_index_t idx = -1;

    action send( PortId_t port ) {
        ig_tm_md.ucast_egress_port = port;
    }

    action drop() {
        ig_dprsr_md.drop_ctl = 1;
    }

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
            // idx used to perform a range match cannot be bit<32> b/c
            // error: : Currently in p4c, the table gradient_addition_pos_t_0 cannot perform a range match on key 
            // ingress::hdr.mlaas.idx as the key does not fit in under 5 PHV nibbles
            idx = ( pool_index_t ) hdr.mlaas.idx;

            // Cannot put the following three lines into an action block b/c
            // error: gradient_addition_neg_t.apply: apply cannot be called from actions
            // gradient_addition_neg_t.apply(); // negative gradient

            // Gradient aggregation
            gradient_addition_pos_t.apply(); // positive gradient
            gradient_addition_neg_t.apply(); // negative gr/adient
            increment_worker();
            
            // send( 2 );

            grad_send_t.apply();
        }
    }
}