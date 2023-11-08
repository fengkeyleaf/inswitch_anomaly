const bit<16> TYPE_IPV4 = 0x800;
const int<32> MAX_COUNT = 1000;
const int<32> MAX_TLS = MAX_COUNT * MAX_COUNT + 1; // count * ( 1000 - tls ) = 1000 * ( 1000 - 0 )
const bit<32> ARRAY_LEN = 6; // legth of the registers( arraies ) in the sketch.

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

typedef int<32> int32;