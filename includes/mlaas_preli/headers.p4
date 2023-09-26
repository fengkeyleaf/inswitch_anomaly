/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

header ethernet_h {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_h {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

// TODO: if a client doesn't the trainning data for a certain parameter,
// do we count this client? i.e. # of grads plus one?
header mlass_h {
    bit<16> idx; // Param index
    int32 grad; // Gradient for the param
    bit<16> number_of_worker; // Number of worker to get the average gradient.
}

struct headers {
    ethernet_h   ethernet;
    ipv4_h       ipv4;
    mlass_h      mlass;
}

struct metadata {

}