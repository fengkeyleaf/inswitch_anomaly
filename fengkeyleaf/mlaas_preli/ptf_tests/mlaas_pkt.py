from scapy.all import IP, IntField, ShortField, BitField, Packet, bind_layers

# TODO: Combine multiple files into one.
# https://scapy.readthedocs.io/en/latest/build_dissect.html
# https://scapy.readthedocs.io/en/latest/api/scapy.fields.html#scapy.fields.BitField
class Mlaas_p( Packet ):
    name = "Mlaas packet"
    fields_desc = [
        IntField( "idx", 0 ),
        # Be careful: SignedIntField and intField.
        IntField( "gradPos", 0 ),
        IntField( "gradNeg", 0 ),
        BitField( "sign", 0, 1 ),
        BitField( "reserves", 0, 7 ),
        ShortField( "numberOfWorker", 0 )
    ]

bind_layers( IP, Mlaas_p )