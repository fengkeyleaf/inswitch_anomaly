const bit<16> TYPE_IPV4 = 0x800;
const int<32> MAX_COUNT = 1000;
const int<32> MAX_TLS = 1000 * 1000 + 1; // count * ( 1000 - tls ) = 1000 * ( 1000 - 0 )

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

typedef int<32> int32;