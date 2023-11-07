/* -*- P4_16 -*- */
#include <core.p4>
// Tofino switch architecture
#include <tna.p4>

// Other p4 files cannot be in the same folder where the entry file is located.
// Otheriwse, complier error.
#include "./includes/mlaas_tonifo/defines.p4"
#include "./includes/mlaas_tonifo/headers.p4"
#include "./includes/mlaas_tonifo/parser.p4"
#include "./includes/mlaas_tonifo/checksum.p4"
#include "./includes/mlaas_tonifo/ingress.p4"
#include "./includes/mlaas_tonifo/deparser.p4"
#include "./includes/mlaas_tonifo/engress.p4"


/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

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