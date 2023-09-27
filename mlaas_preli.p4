/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

// Other p4 files cannot be in the same folder where the entry file is located.
// Otheriwse, complier error.
#include "./includes/mlaas_preli/defines.p4"
#include "./includes/mlaas_preli/headers.p4"
#include "./includes/mlaas_preli/parser.p4"
#include "./includes/mlaas_preli/checksum.p4"
#include "./includes/mlaas_preli/ingress.p4"
#include "./includes/mlaas_preli/deparser.p4"
#include "./includes/mlaas_preli/engress.p4"

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