/* -*- P4_16 -*- */
#include <core.p4>
// Tofino switch architecture
#include <tna.p4>

// . ~/tools/set_sde.bash
// ~/tools/p4_build.sh ~/inswitch_anomaly/inswitch_anomaly/tofino/mlaas_preli.p4 -I/root/inswitch_anomaly/inswitch_anomaly/tofino/mlaas -DMY_VAR=1
// sudo $SDE_INSTALL/bin/veth_setup.sh
//  . ./bf-sde-9.12.0/run_tofino_model.sh -p p4calc
// . ./bf-sde-9.12.0/run_switchd.sh -p p4calc
//  . ./bf-sde-9.12.0/run_bfshell.sh

// Other p4 files cannot be in the same folder where the entry file is located.
// Otheriwse, complier error.
// Note that ERROR: All the attempts to run CPP on /root/inswitch_anomaly/inswitch_anomaly/tofino/mlaas_preli.p4 failed.
// if some include files not found.
#include "mlaas/defines.p4"
#include "mlaas/headers.p4"
#include "mlaas/ingressParser.p4"
#include "mlaas/ingress.p4"
#include "mlaas/ingressDeparser.p4"
#include "mlaas/egressParser.p4"
#include "mlaas/egress.p4"
#include "mlaas/egressDeparser.p4"


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