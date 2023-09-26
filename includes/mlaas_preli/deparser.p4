/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser( packet_out pkt, in headers hdr ) {
    apply {
        pkt.emit( hdr.ethernet );
        pkt.emit( hdr.ipv4 );
        pkt.emit( hdr.mlass );
    }
}