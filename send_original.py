#!/usr/bin/env python3
import random
import socket
import sys

from scapy.all import IP, TCP, Ether, get_if_hwaddr, get_if_list, sendp, bind_layers

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


def send_TCP_pkt( iface, addr ):
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) / sys.argv[2]
    pkt.show2()
    return pkt


def send_mlaas_pkt( iface, addr ):
    pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
    pkt = pkt /IP(dst=addr) / mlass_pkt.Mlaas_p( idx = 0, grad = 1, numberOfWorker = 0 ) / sys.argv[2]
    pkt.show2()
    return pkt


def main():

    if len(sys.argv)<3:
        print('pass 2 arguments: <destination> "<message>"')
        exit(1)

    addr = socket.gethostbyname(sys.argv[1])
    iface = get_if()

    print("sending on interface %s to %s" % (iface, str(addr)))
    pkt = send_TCP_pkt( iface, addr )
    # pkt = send_mlaas_pkt( iface, addr )
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()