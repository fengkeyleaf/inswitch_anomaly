/* -*- P4_16 -*- */
#include <core.p4>
// Tofino switch architecture
#include <tna.p4>

// Other p4 files cannot be in the same folder where the entry file is located.
// Otheriwse, complier error.
#include "./includes/tofino/defines.p4"
#include "./includes/tofino/headers.p4"
#include "./includes/tofino/functions.p4"
#include "./includes/tofino/parser.p4"
#include "./includes/tofino/checksum.p4"
#include "./includes/tofino/sketch.p4" // SKetching algorithm for p4 in-swtich.
#include "./includes/tofino/ingress.p4"
#include "./includes/tofino/egress.p4"
#include "./includes/tofino/deparser.p4"

// Reference material about basic decision-tree combing packet re-forwading:
// https://github.com/cucl-srg/IIsy
// Reference material about basic p4 inswitch anomaly detection:
// https://github.com/sdb2139/p4_inswitch_anomaly

/* *********** F I N A L   P A C K A G E ***************************** */
// Tofino switch architecture
Pipeline(
    IngressParser(),
    Ingress(),
    IngressDeparser(),
    EgressParser(),
    Egress(),
    EgressDeparser()
) pipe;

Switch( pipe ) main;