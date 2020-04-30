from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result
import sys
import logging


"""
##############################
#                            #
#  Usage:   day2.py [<MAC>]  #
#                            #
##############################
"""


# global var
mac_found = False


def collect(task, mac):
    # 'global' not good, but easiest way
    global mac_found

    try:
        # Looking for MAC address in table
        # will not specify MAC as argument in command to use advantages of TextFSM and
        # to avoid checking correctness of MAC syntax
        output = task.run(netmiko_send_command, command_string='show mac address-table', use_textfsm=True)
        for out in output[0].result:
            if out['destination_address'] == mac.lower():
                dest_port = out['destination_port']
                output1 = task.run(netmiko_send_command, command_string='show interface status', use_textfsm=True)

                # Check if it's access port and ignore trunk ports
                for out1 in output1[0].result:
                    if out1['port'] == dest_port and out1['vlan'] != 'trunk':
                        mac_found = True
                        print(f"FOUND: {mac} -- {task.host.name} -- {dest_port}")
                        return

                #print(f"DEBUG: found on trunk port: {mac} -- {task.host.name} -- {dest_port}")
                return

        #print(f"DEBUG: On '{task.host.name}' MAC not found")
    except Exception as e:
        print(f"Something is wrong with '{task.host.name}'")


def main(mac):
    nr = InitNornir(config_file="inventory.yaml")
    nr.run(collect, mac=mac)
    if not mac_found:
        print("MAC not found")


if __name__ == '__main__':
    # Hide Nornir's tracebacks
    logging.getLogger("nornir").addHandler(logging.NullHandler())
    logging.getLogger("nornir").propagate = False

    if len(sys.argv) > 1:
        # assume that second argument is MAC
        mac = sys.argv[1]
    else:
        # no MAC in arguments, ask input here
        mac = input("Enter MAC: ")
        print()

    main(mac)