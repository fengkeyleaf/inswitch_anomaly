/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
// Other p4 files cannot be in the same folder where the entry file is located.
// Otheriwse, complier error.
#include "./includes/headers.p4"
#include "./includes/parser.p4"
#include "./includes/checksum.p4"
#include "./includes/ingress.p4"
#include "./includes/egress.p4"
#include "./includes/deparser.p4"

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
