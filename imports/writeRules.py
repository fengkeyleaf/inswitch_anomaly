import sys

#######################
# Add match-table units.
#######################

# Ipv4 forwarding rules.
def get_actionpara(action):
    para = {}
    if action == 0:
        para = {}
    elif action == 1:
        para = { "dstAddr": "08:00:00:00:01:11", "port": 1 }
    elif action == 2:
        para = { "dstAddr": "08:00:00:00:02:22", "port": 2 }
    elif action == 3:
        para = { "dstAddr": "08:00:00:00:03:33", "port": 3 }
    elif action == 4:
        para = { "dstAddr": "08:00:00:00:04:44", "port": 4 }

    return para


def writeForwardingRules( p4info_helper, sw, range, port ):
    para = get_actionpara( port )
    print( range, para )
    table_entry = p4info_helper.buildTableEntry(
        table_name = "MyIngress.ipv4_lpm",
        match_fields = {
            "hdr.ipv4.dstAddr": range
        },
        action_name = "MyIngress.ipv4_forward",
        action_params = para
    )
    sw.WriteTableEntry(table_entry)
    print("Installed forwarding rule on %s" % sw.name)


# Decision tree rules.

def writeactionrule(p4info_helper, switch, a, b, c, action, port):
    para = get_actionpara(port)
    print( "A: a=%s, b=%s, c=%s, action=%s, para=%s" % ( a, b, c, action, para ) )
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.decision_tree",
        match_fields={
            "meta.src_count_select": a,
            "meta.src_tls_select": b,
            "meta.dst_count_select": c
        },
        action_name=action,
        action_params=para,
        # priority is required, otherwise gRPC unknown error.
        # https://forum.p4.org/t/p4-match-action-tables-with-range-as-the-match-kind/151/5
        priority=1
    )
    switch.WriteTableEntry(table_entry)
    print("Installed action rule on %s" % switch.name)

def writefeature1rule(p4info_helper, switch, range, ind):
    print( "F1: range=%s, ind=%s" % ( range, ind ) )
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.s.src_count_select_t",
        match_fields={
            "scv": range},
        action_name="MyIngress.s.src_count_select_a",
        action_params={
            "v": ind,
        },
        priority=1
    )
    switch.WriteTableEntry(table_entry)
    print("Installed feature1 rule on %s" % switch.name)


def writefeature2rule(p4info_helper, switch, range, ind):
    print( "F2: range=%s, ind=%s" % ( range, ind ) )
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.s.src_tls_select_t",
        match_fields={
            "stv": range},
        action_name="MyIngress.s.src_tls_select_a",
        action_params={
            "v": ind,
        },
        priority=1
    )
    switch.WriteTableEntry(table_entry)
    print("Installed feature2 rule on %s" % switch.name)


def writefeature3rule(p4info_helper, switch, range, ind):
    print( "F3: range=%s, ind=%s" % ( range, ind ) )
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.s.dst_count_select_t",
        match_fields={
            "dcv": range},
        action_name="MyIngress.s.dst_count_select_a",
        action_params={
            "v": ind,
        },
        priority=1
    )
    switch.WriteTableEntry(table_entry)
    print("Installed feature3 rule on %s" % switch.name)

#
# Print out a switch information.
#

def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print('\n----- Reading tables rules for %s -----' % sw.name)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs in the entry to names
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print('%s: ' % table_name, end=' ')
            for m in entry.match:
                print(p4info_helper.get_match_field_name(table_name, m.field_id), end=' ')
                print('%r' % (p4info_helper.get_match_field_value(m),), end=' ')
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print('->', action_name, end=' ')
            for p in action.params:
                print(p4info_helper.get_action_param_name(action_name, p.param_id), end=' ')
                print('%r' % p.value, end=' ')
            print()


def printGrpcError(e):
    print("gRPC Error:", e.details(), end=' ')
    status_code = e.code()
    print("(%s)" % status_code.name, end=' ')
    traceback = sys.exc_info()[2]
    print("[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))


#######################
# Writing process.
#######################


def writeBasicForwardingRules( p4info_helper, s1 ):
    R = [ ( "10.0.1.1", 32 ), ( "10.0.2.2", 32 ), ( "10.0.3.3", 32 ), ( "10.0.4.4", 32 ) ]
    P = [ 1, 2, 3, 4 ]
    for i in range( len( R ) ):
        print( R[ i ], P[ i ] )
        writeForwardingRules( p4info_helper, s1, R[ i ], P[ i ] )


def writeMLRules( 
    classfication, protocol, srouce, 
    dstination, action, p4info_helper,
    s1, proto, src, dst
):
    for i in range(len(classfication)):
        a = protocol[i]
        id = len(a) - 1
        del a[1:id]
        if (len(a) == 1):
            a.append(a[0])
        b = srouce[i]
        id = len(b) - 1
        del b[1:id]
        if (len(b) == 1):
            b.append(b[0])
        c = dstination[i]
        id = len(c) - 1
        del c[1:id]
        if (len(c) == 1):
            c.append(c[0])

        ind = int(classfication[i])
        ac = action[ind]
        a = [i + 1 for i in a]
        b = [i + 1 for i in b]
        c = [i + 1 for i in c]

        if ac == 0:
            writeactionrule(p4info_helper, s1, a, b, c, "MyIngress.drop", 0)
        else:
            writeactionrule(p4info_helper, s1, a, b, c, "MyIngress.ipv4_forward", ac)

    if len(proto) != 0:
        proto.append(0)
        proto.append(32)
        proto.sort()
        for i in range(len(proto) - 1):
            writefeature1rule(p4info_helper, s1, proto[i:i + 2], i + 1)
    else:
        writefeature1rule(p4info_helper, s1, [0, 32], 1)

    if len(src) != 0:
        src.append(0)
        src.append(65535)
        src.sort()
        for i in range(len(src) - 1):
            writefeature2rule(p4info_helper, s1, src[i:i + 2], i + 1)
    if len(dst) != 0:
        dst.append(0)
        dst.append(65535)
        dst.sort()
        for i in range(len(dst) - 1):
            writefeature3rule(p4info_helper, s1, dst[i:i + 2], i + 1)

    # TODO Uncomment the following two lines to read table entries from s1 and s2
    readTableRules(p4info_helper, s1)