// #include "gradient_addition.p4"
// #include "gradient_send.p4"
#include "workerCount.p4"

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
    pool_index_t idx = 0;
    WorkerCount() worker_counter;

    // The type argument I specifies the type of the index of an indirect register extern. 
    // This type can typically be inferred by the compiler.
    // The type argument T specifies the type of each entry, 
    // i.e. the type of state stored in each entry of the register.
    // error: Unsupported Register element type struct grad_v for Ingress.G
    // Supported Register element types:
    //     bit<8> int<8> bit<16> int<16> bit<32> int<32>
    //     structs containing one or two fields of one of the above types
    //     bit<1> bit<64>
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
    // U is the return value type. 
    // error: RegisterAction.execute: RegisterAction return type must be simple (void, bit, bool or enum), not complex
    // extern RegisterAction<T, I, U> {
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
    Register<int<32>, pool_index_t>( POOL_SIZE, 0 ) G; // gradients
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
            // idx used to perform a range match cannot be bit<32> b/c
            // error: : Currently in p4c, the table gradient_addition_pos_t_0 cannot perform a range match on key 
            // ingress::hdr.mlaas.idx as the key does not fit in under 5 PHV nibbles
            idx = ( bit<15> ) hdr.mlaas.idx;

            meta.is_reset = false;
            hdr.mlaas.v = update_grad.execute( idx );
            worker_counter.apply( hdr, meta, ig_tm_md );
        }
    }
}