import json
from typing import Dict


def get_host_json( n: str, i: str, m: str, c:str ) -> Dict:
    return ( n, {
        "ip": i,
        "mac": m,
        "commands": c
    } )


# https://pythonexamples.org/python-write-json-to-file/
def generate_topo_json( H, S, L ):
    """
    :param I: List of hosts and their configurations.
    :param S: List of swtiches and their configurations.
    :param L: List of links and their configurations.
    :return: 
    """
    return json.dumps( {
        "hosts": H,
        "switches": S,
        "links": L
    }, indent = 4 )


def write_to_file( topo, fp ):
    with open( fp, "w+" ) as f:
        f.write( topo )


def get_hosts_json( H: Dict[ str, Dict ] ):
    d = {}
    for k in H.keys():
        
        pass

if __name__ == '__main__':
    H = {}
    S = {}
    L = []
    ( hn, hc ) = get_host_json( "h1", "10.0.1.1/24", "08:00:00:00:01:11", ["route add default gw 10.0.1.10 dev eth0",
                           "arp -i eth0 -s 10.0.1.10 08:00:00:00:01:00"] )
    H[ hn ] = hc
    ( hn, hc ) = get_host_json( "h2", "10.0.2.2/24", "08:00:00:00:02:22", ["route add default gw 10.0.2.20 dev eth0",
                           "arp -i eth0 -s 10.0.2.20 08:00:00:00:02:00"] )
    H[ hn ] = hc
    ( hn, hc ) = get_host_json( "h3", "10.0.3.3/24", "08:00:00:00:03:33", ["route add default gw 10.0.3.30 dev eth0",
                           "arp -i eth0 -s 10.0.3.30 08:00:00:00:03:00"] )
    H[ hn ] = hc
    ( hn, hc ) = get_host_json( "h4", "10.0.4.4/24", "08:00:00:00:04:44", ["route add default gw 10.0.4.40 dev eth0",
                           "arp -i eth0 -s 10.0.4.40 08:00:00:00:04:00"] )
    H[ hn ] = hc
    S[ "s1" ] = {}
    L.append( ["h1", "s1-p1"] )
    L.append( ["h2", "s1-p2"] )
    L.append( ["h3", "s1-p3"] )
    L.append( ["h4", "s1-p4"] )
    print( generate_topo_json( H, S, L ) )
    write_to_file( generate_topo_json( H, S, L ), "../pod-topo/topology.json" )