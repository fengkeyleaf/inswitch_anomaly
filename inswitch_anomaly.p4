/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
// Other p4 files cannot be in the same folder where the entry file is located.
// Otheriwse, complier error.
#include "./includes/defines.p4"
#include "./includes/headers.p4"
#include "./includes/functions.p4"
#include "./includes/parser.p4"
#include "./includes/checksum.p4"
// #include "./includes/sketch.p4"
#include "./includes/ingress.p4"
#include "./includes/egress.p4"
#include "./includes/deparser.p4"

// Reference material about basic decision-tree combing packet re-forwading:
// https://github.com/cucl-srg/IIsy
// Reference material about basic p4 inswitch anomaly detection:
// https://github.com/sdb2139/p4_inswitch_anomaly

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    // Sketch(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
