from scapy.all import IP, IntField, SignedIntField, ShortField, Packet, bind_layers

class Mlaas_p( Packet ):
    name = "Mlaas packet"
    fields_desc = [
        IntField( "idx", 0 ),
        SignedIntField( "grad", 0 ),
        ShortField( "numberOfWorker", 0 )
    ]

bind_layers( IP, Mlaas_p )