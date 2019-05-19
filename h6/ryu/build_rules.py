
import ryu_ofctl

def createFlow(dl_src, dl_dst, in_port, out_port, switch_dpid, priority=50001):
    """
    create the flow and insert to the switch
    :param dl_src: source mac, string
    :param dl_dst: dest mac, string
    :param in_port: in port, integer
    :param out_port: out port for the action, integer
    :return: the FlowEntry object with the associate action of out_port
    """
    flow = ryu_ofctl.FlowEntry()
    # for the constant
    flow.priority = priority
    # http protocol: tcp and port 80
    flow.dl_type = 0x800  # IPV4
    flow.nw_proto = 0x6 # TCP
    flow.tp_dst = 80 # webserver port
    # for src and dest mac
    flow.dl_src = dl_src
    flow.dl_dst = dl_dst
    # for in and out_port
    flow.in_port = in_port
    act = ryu_ofctl.OutputAction(out_port)
    # add the action to the flow
    flow.addAction(act)
    # insert the flow to the switch
    print("the flow is")
    flow.printMatch()
    print(ryu_ofctl.insertFlow(switch_dpid, flow))
    return flow

# list the mac of each machine
mac1 = "02:35:19:b7:3e:f7"  # h1
mac2 = "6e:1d:53:54:d9:e7"  # h2
mac3 = "52:1c:b7:87:b2:bd"  # h3

# list of dpids of the switches
sw1 = '0000daed57ae3949'
sw2 = '00002ad84265224b'
sw3 = '00006e3e0e07ca45'

# to get the ports
ryu_ofctl.getMacIngressPort(mac1)
ryu_ofctl.getMacIngressPort(mac2)
ryu_ofctl.getMacIngressPort(mac3)
ryu_ofctl.listLinks()


# writing the flow for the f** switches
# building the topology diagram by checking the links

# From h1 to h3: GW (gateway) to FW (firewall)

h1_s1 = createFlow(dl_src=mac1, dl_dst=mac2, in_port=1, out_port=2, switch_dpid=sw1)
s1_s3 = createFlow(dl_src=mac1, dl_dst=mac2, in_port=1, out_port=2, switch_dpid=sw3)
# s2_h3: no need a rules

#createFlow(dl_src=None, dl_dst=, in_port=, out_port=, switch_dpid=)
# From h3 to h2: FW to WP - wordpress
h3_s3 = createFlow(dl_src=mac1, dl_dst=mac2, in_port=2, out_port=1, switch_dpid=sw3)
s3_s1 = createFlow(dl_src=mac1, dl_dst=mac2, in_port=2, out_port=3, switch_dpid=sw1)
s1_s2 = createFlow(dl_src=mac1, dl_dst=mac2, in_port=1, out_port=2, switch_dpid=sw2)

# From h2 to h3: WP -> FW
h2_s2 = createFlow(dl_src=mac2, dl_dst=mac1, in_port=2, out_port=1, switch_dpid=sw2)
s2_s1 = createFlow(dl_src=mac2, dl_dst=mac1, in_port=3, out_port=2, switch_dpid=sw1)
s1_s3 = createFlow(dl_src=mac2, dl_dst=mac1, in_port=1, out_port=2, switch_dpid=sw3)

# From h3 to h1: FW to GW
h3_s3 = createFlow(priority=50002, dl_src=mac2, dl_dst=mac1, in_port=2, out_port=1, switch_dpid=sw3) # higher
s3_s1 = createFlow(priority=50003,dl_src=mac2, dl_dst=mac1, in_port=2, out_port=1, switch_dpid=sw1)

# to delete all flows
#ryu_ofctl.deleteAllFlows(sw1)
#ryu_ofctl.deleteAllFlows(sw2)
#ryu_ofctl.deleteAllFlows(sw3)