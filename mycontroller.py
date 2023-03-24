#!/usr/bin/env python3
import argparse
import os
import sys
from time import sleep
import grpc

"""
file: 
description:
language: python3 3.8.10
author: Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""

# Reference material about basic decision-tree combing packet re-forwading:
# https://github.com/cucl-srg/IIsy
# Reference material about basic p4 inswitch anomaly detection:
# https://github.com/sdb2139/p4_inswitch_anomaly

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
# sys.path.append(
#     os.path.join(os.path.dirname(os.path.abspath(__file__)),
#                  './utils/'))

import utils.p4runtime_lib.bmv2 as bmv2
import utils.p4runtime_lib.helper as helper
from utils.p4runtime_lib.switch import ShutdownAllSwitchConnections

from imports.ml import find_action, find_classification, find_feature
from imports.write_rules import writeBasicForwardingRules, writeMLRules, printGrpcError

#######################
# Paraphrase ML model.
#######################


inputfile = '../decision_tree/tree.txt'
inputfile = "./test/test_tree_4_features.txt"
actionfile = '../decision_tree/action.txt'
actionfile = "./config/action.txt"

fr = r"(srcCount|srcTLS|dstCount|dstTLS)"
FS = [ "srcCount", "srcTLS", "dstCount", "dstTLS" ]

srcCount, srcTLS, dstCount, dstTLS = find_feature( inputfile, len( FS ) )
print( "Feature:\nsrcCount=%s, srcTLS=%s, dstCount=%s, dstTLS=%s" % ( srcCount, srcTLS, dstCount, dstTLS ) )
srcCountMap, srcTLSMap, dstCountMap, dstTLSMap, classfication = find_classification( inputfile, [ srcCount, srcTLS, dstCount, dstTLS ], FS, fr )
print( "Classification:\nsrcCountMap=%s, srcTLSMap=%s, dstCountMap=%s, dstTLSMap=%s, class=%s" % ( srcCountMap, srcTLSMap, dstCountMap, dstTLSMap, classfication ) )
action = find_action( actionfile )
print( "Action: %s" % ( action ) )


#######################
# Contorl plane process.
#######################


def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        # s2.MasterArbitrationUpdate()

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s1")

        # Write basic forwarding rules into switch.
        # writeBasicForwardingRules( p4info_helper, s1 )

        writeMLRules(
            srcCount = srcCount,
            srcCountMap = srcCountMap,
            srcTLS = srcTLS,
            srcTLSMap = srcTLSMap,
            dstCount = dstCount,
            dstCountMap = dstCountMap,
            dstTLS = dstTLS,
            dstTLSMap = dstTLSMap,
            classfication = classfication,
            action = action,
            s1 = s1,
            p4info_helper = p4info_helper
        )

    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/inswitch_anomaly.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/inswitch_anomaly.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)

    main(args.p4info, args.bmv2_json)
