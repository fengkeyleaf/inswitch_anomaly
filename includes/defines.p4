const bit<16> TYPE_IPV4 = 0x800;
const int<32> MAX_COUNT = 1000;
const int<32> MAX_TLS = MAX_COUNT * MAX_COUNT + 1; // count * ( 1000 - tls ) = 1000 * ( 1000 - 0 )
// legth of the registers( arraies ) in the sketch.
// Also the limitation of the sketch.
// Half of the array is used by src IPs while the other half of it is used by dst IPs
const bit<32> ARRAY_LEN = 16; 

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

typedef int<32> int32;