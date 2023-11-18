control WorkerCount( 
    /* User */
    inout my_ingress_headers_t                       hdr,
    inout my_ingress_metadata_t                      meta,
    /* Intrinsic */
    inout ingress_intrinsic_metadata_for_tm_t        ig_tm_md
) {
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
    
    Register<bit<16>, pool_index_t>( POOL_SIZE, 0 ) C; // Worker count
    RegisterAction<bit<16>, pool_index_t, bit<16>>( reg = C ) update_count = {
        void apply( inout bit<16> v, out bit<16> rv ) {
            if ( v == NUMBER_OF_WORKER ) {
                v = 1;
            }
            else {
                v = v + 1;
            }

            rv = v;
        }
    };

    apply {
        hdr.mlaas.numberOfWorker = update_count.execute( meta.idx );

        if ( hdr.mlaas.numberOfWorker == 1 ) {
            meta.is_reset = true;
        }
        else {
            meta.is_reset = false;
        }
    }
}