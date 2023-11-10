/*************************************************************************
 ************* C O N S T A N T S    A N D   T Y P E S  *******************
**************************************************************************/

const bit<16> TYPE_IPV4 = 0x800;
const bit<32> POOL_SIZE = 256;
const bit<16> NUMBER_OF_WORKER = 2;
const bit<32> MAX_UNSIGNED_INT = ( bit<32> ) -1;

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

typedef bit<32> unsigned_int32;