/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress( inout headers hdr,
                   inout metadata meta,
                   inout standard_metadata_t standard_metadata ) {
    action drop() {
        mark_to_drop( standard_metadata );
    }

    action ipv4_forward( macAddr_t dstAddr, egressSpec_t port ) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action set_actionselect1( bit<14> featurevalue1 ) {
        meta.action_select1 = featurevalue1;

   }

    action set_actionselect2( bit<14> featurevalue2 ) {
        meta.action_select2 = featurevalue2;

   }

    action set_actionselect3( bit<14> featurevalue3 ) {
        meta.action_select3 = featurevalue3;
   }

   table feature1_exact {
        key = {
            hdr.ipv4.protocol : range ;
        }

        actions = {
	        NoAction;
            set_actionselect1;
        }

        size = 1024;
    } 

    table feature2_exact {
        key = {
            hdr.tcp.srcPort : range ;
        }

        actions = {
	        NoAction;
            set_actionselect2;
        }

        size = 1024;
    }

    table feature3_exact {
        key = {
            hdr.tcp.dstPort : range ;
        }

        actions = {
	        NoAction;
            set_actionselect3;
        }

        size = 1024;
    }

    table ipv4_exact {
        key = {
            meta.action_select1: range;
            meta.action_select2: range;
            meta.action_select3: range;
	    }

        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
	
        size = 1024;
        default_action = drop();
    }

    apply {
        if ( hdr.ipv4.isValid() ) {
            feature1_exact.apply();
            if( hdr.ipv4.protocol == 6 ) {
                feature2_exact.apply();
                feature3_exact.apply();
            }
            else {
                meta.action_select2 = 1;
                meta.action_select3 = 1;
            }   
	    }
        
	    ipv4_exact.apply();
    }
}