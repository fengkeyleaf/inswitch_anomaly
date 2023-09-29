#!/usr/bin/env python3
import random
import socket
import sys

from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp

import mlass_pkt


def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface


def get_TCP_pkt( iface, addr ):
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt / IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / sys.argv[2]
    pkt.show2()
    return pkt


def send_TCP_pkt( iface, addr ):
    pkt = get_TCP_pkt( iface, addr )
    sendp(pkt, iface=iface, verbose=False)


def get_mlaas_pkt( iface, addr, idx: int, gradPos: int, gradNeg: int, sign: bool, number_of_worker: int ):
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt / IP(dst=addr) / mlass_pkt.Mlaas_p( 
        idx = idx, gradPos = gradPos, gradNeg = gradNeg, sign = sign
    )
    pkt.show2()
    return pkt


# ( pos_grad, neg_grad, # of workers ) = ( 10, 0, 2 )
def send_mlaas_2pkts_case1( iface, addr ):
    pkt = get_mlaas_pkt( iface, addr, 0, 5, 0, False, 0 )
    sendp( pkt, iface = iface, verbose = False )
    pkt = get_mlaas_pkt( iface, addr, 0, 5, 0, False, 0 )
    sendp( pkt, iface = iface, verbose = False )


# ( pos_grad, neg_grad, # of workers ) = ( 100100, 0, 2 )
def send_mlaas_2pkts_case2( iface, addr ):
    pkt = get_mlaas_pkt( iface, addr, 0, 100, 0, False, 0 )
    sendp( pkt, iface = iface, verbose = False )
    pkt = get_mlaas_pkt( iface, addr, 0, 100000, 0, False, 0 )
    sendp( pkt, iface = iface, verbose = False )


# ( pos_grad, neg_grad, # of workers ) = ( 0, 20, 2 )
def send_mlaas_2pkts_case3( iface, addr ):
    pkt = get_mlaas_pkt( iface, addr, 0, 1, 5, True, 0 )
    sendp( pkt, iface = iface, verbose = False )
    pkt = get_mlaas_pkt( iface, addr, 0, 2, 15, True, 0 )
    sendp( pkt, iface = iface, verbose = False )


# ( pos_grad, neg_grad, # of workers ) = ( 0, 11000000, 2 )
def send_mlaas_2pkts_case4( iface, addr ):
    pkt = get_mlaas_pkt( iface, addr, 0, 1, 1000000, True, 0 )
    sendp( pkt, iface = iface, verbose = False )
    pkt = get_mlaas_pkt( iface, addr, 0, 2, 10000000, True, 0 )
    sendp( pkt, iface = iface, verbose = False )


# ( pos_grad, neg_grad, # of workers ) = ( 10, 5, 2 )
def send_mlaas_2pkts_case5( iface, addr ):
    pkt = get_mlaas_pkt( iface, addr, 0, 10, 0, False, 0 )
    sendp( pkt, iface = iface, verbose = False )
    pkt = get_mlaas_pkt( iface, addr, 0, 0, 5, True, 0 )
    sendp( pkt, iface = iface, verbose = False )


# ( pos_grad, neg_grad, # of workers ) = ( 50, 1000000, 2 )
def send_mlaas_2pkts_case6( iface, addr ):
    pkt = get_mlaas_pkt( iface, addr, 0, 0, 1000000, True, 0 )
    sendp( pkt, iface = iface, verbose = False )
    pkt = get_mlaas_pkt( iface, addr, 0, 50, 0, False, 0 )
    sendp( pkt, iface = iface, verbose = False )


# idx -> ( pos_grad, neg_grad, # of workers ) = 0 -> ( 0, 10, 1 )
# 1 -> ( 50, 0, 1 )
def send_mlaas_pkts_2hosts_1( iface, addr ):
    pkt = get_mlaas_pkt( iface, addr, 0, 0, 10, True, 0 )
    sendp( pkt, iface = iface, verbose = False )
    pkt = get_mlaas_pkt( iface, addr, 1, 50, 0, False, 0 )
    sendp( pkt, iface = iface, verbose = False )


# 0 -> ( 30, 0, 2 )
# 1 -> ( 0, 40, 2 )
def send_mlaas_pkts_2hosts_2( iface, addr ):
    pkt = get_mlaas_pkt( iface, addr, 0, 30, 0, False, 0 )
    sendp( pkt, iface = iface, verbose = False )
    pkt = get_mlaas_pkt( iface, addr, 1, 0, 40, True, 0 )
    sendp( pkt, iface = iface, verbose = False )

# Final result:
# 0 -> ( 30, 10, 2 )
# 1 -> ( 50, 40, 2 )

def main():
    if len(sys.argv)<3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))
    # send_TCP_pkt( iface, addr )

    # send_mlaas_2pkts_case1( iface, addr )
    # send_mlaas_2pkts_case2( iface, addr )
    # send_mlaas_2pkts_case3( iface, addr )
    # send_mlaas_2pkts_case4( iface, addr )
    # send_mlaas_2pkts_case5( iface, addr )
    # send_mlaas_2pkts_case6( iface, addr )
    # send_mlaas_pkts_2hosts_1( iface, addr )
    send_mlaas_pkts_2hosts_2( iface, addr )


if __name__ == '__main__':
    main()