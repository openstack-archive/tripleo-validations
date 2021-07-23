#!/usr/bin/env python

# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""get_dpdk_nics_numa_info module
Used by the `check_nfv_ovsdpdk_zero_packet_loss` role.
"""

from ansible.module_utils.basic import AnsibleModule
from yaml import safe_load as yaml_safe_load

import json
import yaml

DOCUMENTATION = '''
---
module: DPDK NIC's NUMA details
short_description: Gets the DPDK NIC's NUMA details
description:
    - Gets the DPDK NIC's NUMA details
    - Owned by the DFG:NFV Integration
options:
    dpdk_mapping_file:
        required: true
        description:
           - The DPDK mapping file path
        type: str

author: "Jaganathan Palanisamy"
'''

EXAMPLES = '''
# Call this module from TripleO Ansible Validations

- name: Get DPDK NIC's NUMA info
  become: true
  get_dpdk_nics_numa_info:
    dpdk_mapping_file: /var/lib/os-net-config/dpdk_mapping.yaml
  register: dpdk_nics_numa
'''


def get_dpdk_nics_mapping(module, dpdk_mapping_file, mac):
    """Gets the DPDK NIC's mapping with NIC physical name and
    driver info for the given MAC."""

    # Reads dpdk mapping file
    cmd = "cat " + dpdk_mapping_file
    result = module.run_command(cmd)
    if (not result or (result[0] != 0) or not (str(result[1]).strip(' '))):
        err = "Unable to determine DPDK NIC's details"
        module.fail_json(msg=err)
    else:
        dpdk_nics_map = yaml.load(str(result[1]), Loader=yaml.SafeLoader)
        for dpdk_nic_map in dpdk_nics_map:
            if dpdk_nic_map['mac_address'] == mac:
                return dpdk_nic_map
        else:
            err = ("Unable to determine DPDK NIC Mapping for MAC: '%(mac)s'" % {'mac': mac})
            module.fail_json(msg=err)


def get_dpdk_nics_info(module, dpdk_mapping_file):
    """Gets the DPDK NIC's information like interface name, pci,
    mac and mtu etc.. using dpdk mapping file."""

    dpdk_nics_info = []
    dpdk_nics = []
    # Gets the DPDK interfaces details
    cmd = "ovs-vsctl --columns=name,type,admin_state --format=json list interface"
    result = module.run_command(cmd)
    if (not result or (result[0] != 0) or not (str(result[1]).strip(' '))):
        err = "Unable to determine DPDK NIC's details"
        module.fail_json(msg=err)
    else:
        nics = json.loads(str(result[1]))
        for nic in nics.get('data', []):
            if nic and str(nic[1]) == 'dpdk' and str(nic[2]) == 'up':
                dpdk_nics.append(str(nic[0]))
        if dpdk_nics:
            # Gets the mac, mtu and status information of all the DPDK interfaces
            cmd = ("ovs-vsctl --column=mac-in-use,mtu,status --format=json "
                   "list interface " + ' '.join(dpdk_nics))
            result = module.run_command(cmd)
            if (not result or (result[0] != 0) or not (str(result[1]).strip(' '))):
                err = "Unable to determine DPDK NIC's details"
                module.fail_json(msg=err)
            else:
                nics_info = json.loads(str(result[1]))
                for nic_info in nics_info.get('data', []):
                    data = {}
                    data['mac'] = nic_info[0]
                    data['mtu'] = nic_info[1]
                    for field in nic_info[2][1]:
                        if field[0] == 'numa_id':
                            data['numa_node'] = int(field[1])
                    dpdk_nic_map = get_dpdk_nics_mapping(module, dpdk_mapping_file, nic_info[0])
                    #data['nic'] = dpdk_nic_map['name']
                    data['pci'] = dpdk_nic_map['pci_address']
                    dpdk_nics_info.append(data)
        return dpdk_nics_info


def get_dpdk_nics_numa_info(module, dpdk_mapping_file):
    """Gets the DPDK NIC's NUMA info."""

    result = dict(
        changed=False,
        dpdk_nics_numa_info=[],
        message=''
    )
    dpdk_nics_info = get_dpdk_nics_info(module, dpdk_mapping_file)
    if not dpdk_nics_info:
        err = "Unable to determine DPDK NIC's NUMA info"
        module.fail_json(msg=err)
    else:
        result['message'] = "DPDK NIC's NUMA info"
        result['dpdk_nics_numa_info'] = dpdk_nics_info
        module.exit_json(**result)


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

    get_dpdk_nics_numa_info(module,
                            module.params.get('dpdk_mapping_file'))


if __name__ == '__main__':
    main()
