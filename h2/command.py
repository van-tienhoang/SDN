#!/usr/bin/env python
import time
import sys
import argparse
import logging
import json
import requests

base_url = 'http://localhost:8181/onos/v1/'


def flow_template(deviceide, outport, inport):
    """return the json flow format

    Arguments:
        deviceide {string} -- device id
        outport {string} -- output port of the device
        inport {string/interger} -- input port of the device
        the arguments could be in string and/or integer format

    Returns:
        dict -- the json flow rule
    """

    content = {
        "priority": 40001,
        "timeout": 0,
        "isPermanent": True,
        "deviceId": deviceide,
        "treatment": {
            "instructions": [
              {
                  "type": "OUTPUT",
                  "port": outport
              }
            ]
        },
        "selector": {
            "criteria": [
                {
                    "type": "IN_PORT",
                    "port": inport
                }
            ]
        }
    }
    return content


def flow_template_with_mac(deviceid, outport, inport, mac_src, mac_dst):
    """similar to flow_template, but use for the switch which connects to the host directly

    Arguments:
        deviceid {[type]} -- device id/switch
        outport {[type]} -- output port
        inport {[type]} -- input port
        mac_src {[type]} -- mac of the sending host
        mac_dst {[type]} -- mac of the receiving host

    Returns:
        dict -- json template
    """

    content = {
        "priority": 40001,
        "timeout": 0,
        "isPermanent": True,
        "deviceId": deviceid,
        "treatment": {
            "instructions": [
              {
                  "type": "OUTPUT",
                  "port": outport
              }
            ]
        },
        "selector": {
            "criteria": [
                {
                    "type": "IN_PORT",
                    "port": inport
                },
                {
                    "type": "ETH_SRC",
                    "mac": mac_src
                },
                {
                    "type": "ETH_DST",
                    "mac": mac_dst
                }
            ]
        }
    }
    return content


def get_two_paths(host_1, host_2, base_url='http://localhost:8181/onos/v1'):
    """get the paths between host 1 and host 2, bi-drectional path

    Arguments:
        host_1 {[type]} -- host 1 id
        host_2 {[type]} -- host 2 id

    Keyword Arguments:
        base_url {string} -- url to the onos restful service (default: {'http://localhost:8181/onos/v1'})

    Returns:
        two dicts -- one dictionary is the forward path (host1-->host2), the 2nd dictionary is path (host2-->host1)
    """

    host1_sw, host1_inport, host1_mac = get_host_info(host_1)
    host2_sw, host2_inport, host2_mac = get_host_info(host_2)

    url = base_url + '/paths/' + host1_sw + '/' + host2_sw
    print(url)
    res = requests.get(url, auth=('onos', 'rocks'))
    paths = res.json()

    # get the reverse path
    paths2 = requests.get(base_url + '/paths/' + host2_sw +
                          '/' + host1_sw, auth=('onos', 'rocks'))

    return paths, paths2.json()


def get_switch_id_from_host_id(host_id, base_url='http://localhost:8181/onos/v1/'):
    response = requests.get(base_url + 'hosts/' +
                            host_id, auth=('onos', 'rocks'))
    print(base_url + 'hosts/' + host_id)
    res = response.json()
    switch_id = res['locations'][0]['elementId']
    switch_inport = res['locations'][0]['port']
    host_mac = res['mac']
    return switch_id, switch_inport, host_mac


def get_host_info(host_id, base_url='http://localhost:8181/onos/v1/'):
    """get the information of host

    Arguments:
        host_id {[type]} -- host id

    Keyword Arguments:
        base_url {str} -- restful url (default: {'http://localhost:8181/onos/v1/'})

    Returns:
        tuples -- switch id, port of the connected switch, mac of the switch
    """

    return get_switch_id_from_host_id(host_id, base_url)


def get_path_and_install_flow(host_1, host_2, paths, base_url='http://localhost:8181/onos/v1'):
    """get the paths and install the flows

    Arguments:
        host_1 {[type]} -- [description]
        host_2 {[type]} -- [description]
        paths {[type]} -- the 2 paths host1-->host2 and host2-->host1 (from get_two_paths)

    Keyword Arguments:
        base_url {str} -- [description] (default: {'http://localhost:8181/onos/v1'})
    """

    host1_sw, host1_inport, host1_mac = get_host_info(host_1)
    print(host1_sw, host1_inport, host1_mac)

    host2_sw, host2_inport, host2_mac = get_host_info(host_2)
    print(host2_sw, host2_inport, host2_mac)

    print('Number of path(s)  ' + str(len(paths)))
    # for all paths ==> todo: there is only one path
    # for 1st link in the path
    if(len(paths['paths']) < 1):
        return 1
    links = paths['paths'][0]['links']
    print('number of link(s) ' + str(len(links)))
    first_link = links[0]
    outport = first_link['src']['port']
    json_host_1 = flow_template_with_mac(
        host1_sw, outport, host1_inport, host1_mac, host2_mac)
    # POST
    flow_url = base_url + '/flows/'
    r = requests.post(flow_url + host1_sw,
                      data=json.dumps(json_host_1),  auth=('onos', 'rocks'))
    print(r)
    print(json_host_1)
    # print(json_host_1)
    print("finish creating 1st flow")
    # for all other rules in the middle
    for index in range(1, len(links)):
        inport = links[index-1]['dst']['port']
        outport = links[index]['src']['port']
        device_id = links[index]['src']['device']
        json_switch = flow_template(device_id, outport, inport)
        print(json_switch)
        r = requests.post(flow_url + device_id,
                          data=json.dumps(json_switch), auth=('onos', 'rocks'))

        print(r)
        # print(json_switch)

    #  create the flow rule to host2
    last_link = links[-1]
    inport = last_link['dst']['port']
    outport = host2_inport
    device_id = host2_sw
    json_last = flow_template(device_id, outport, inport)
    #print("last \n" + json_last)
    r = requests.post(flow_url + device_id,
                      data=json.dumps(json_last), auth=('onos', 'rocks'))
    print(r)
    # print(json_last)


def check_port(device, port_device):
    """check if the port of the device is disable

    Arguments:
        device {string} -- device ide
        port_device {string} -- port number, in string format
    """
    url = base_url + '/devices/' + device + '/ports'
    print(url)
    res = requests.get(url, auth=('onos', 'rocks'))
    print(res.status_code)
    if (res.status_code != 200):
        pass
    ports = res.json()['ports']
    print(ports)
    for port in ports:
        if port['port'] != port_device:
            continue
        if port['isEnabled'] == True:
            continue
        if (port['port'] == port_device) and (port['isEnabled'] == False):
            print("Link failure at switch {0}: port {1}".format(
                device, port_device))
            return False
    return True


def check_link_fail(path):
    """check if any link is failed

    Arguments:
        path {[type]} -- [description]
    """
    if(len(path['paths']) < 1):
        return 1
    links = path['paths'][0]['links']

    for link in links:
        device = link['src']['device']
        port_device = link['src']['port']
        check_port(device, port_device)

        device = link['dst']['device']
        port_device = link['dst']['port']
        check_port(device, port_device)
    print("There is no link fail yet.")


def main(args):

    host_1 = args.host1
    host_2 = args.host2
    base_url = 'http://localhost:8181/onos/v1'
    # host_1, host_2 = '00:00:00:00:00:01/None', '00:00:00:00:00:03/None'

    path_fw, path_bw = get_two_paths(host_1, host_2)
    get_path_and_install_flow(host_1, host_2, path_bw)
    get_path_and_install_flow(host_2, host_1, path_fw)
    print("Finish making bi-directional path.")

    print("start checking links:")

    print("press ctrl-c to stop")
    loop_forever = True
    while loop_forever:
        try:
            time.sleep(5)
            check_link_fail(path_fw)
            check_link_fail(path_bw)
        except KeyboardInterrupt:
            loop_forever = False

    print("Do not implement link recovery yet.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Does a thing to some stuff.",
        epilog="inputs are the host id. Tested on tree topology",
        fromfile_prefix_chars='@')
    parser.add_argument(
        "host1",
        help="ID of host 1",
        metavar="ARG")

    parser.add_argument(
        "host2",
        help="ID of host 2",
        metavar="ARG")

    args = parser.parse_args()
    print(args.host1)
    print(args.host2)
    main(args)
