/*************************************************************************
 ************* C O N S T A N T S    A N D   T Y P E S  *******************
**************************************************************************/

// Networking
const bit<16> TYPE_IPV4 = 0x800;

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

// Numbers
const bit<32> MAX_UNSIGNED_INT = ( bit<32> ) -1;
typedef bit<32> unsigned_int32;

// switchML
// https://github.com/p4lang/p4app-switchML/blob/main/dev_root/p4/types.p4#L109
typedef bit<15> pool_index_t;

const bit<32> POOL_SIZE = 256;
const bit<16> NUMBER_OF_WORKER = 1;