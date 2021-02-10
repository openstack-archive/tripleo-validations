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
"""check_cpus_aligned_with_dpdk_nics module
Used by the `check_nfv_ovsdpdk_zero_packet_loss` role.
"""

from ansible.module_utils.basic import AnsibleModule
from yaml import safe_load as yaml_safe_load

import json
import yaml

DOCUMENTATION = '''
---
module: OVS DPDK PMD CPU's check
short_description: Run PMD CPU's from all the NUMA nodes check
description:
    - Run PMD CPU's from all the NUMA nodes check
    - Owned by the DFG:NFV Integration
options:
    cpus:
        required: true
        description:
           - The CPU's list
        type: str
    numa_node:
        required: true
        description:
           - The NUMA node
        type: int
    dpdk_nics_numa_info:
        required: true
        description:
           - The DPDK NIC's NUMA details
        type: list
author: "Jaganathan Palanisamy"
'''

EXAMPLES = '''
# Call this module from TripleO Ansible Validations

- name: Check CPU's aligned with DPDK NIC's NUMA
  become: true
  check_cpus_aligned_with_dpdk_nics:
    cpus: "2,3,4,5"
    numa_node: "0"
    dpdk_nics_numa_info: [{"numa_node": 0, "mac": "mac1", "pci": "pci1"},
                          {"numa_node": 0, "mac": "mac2", "pci": "pci2"}]
  register: valid_cpus
'''


def get_nodes_cpus_info(module):
    """Gets the logical cpus info for all numa nodes."""

    dict_cpus = {}
    # Gets numa node and cpu details
    cmd = "lscpu -p=NODE,CPU"
    result = module.run_command(cmd)
    if (not result or (result[0] != 0) or not (str(result[1]).strip(' '))):
        err = "Unable to determine NUMA cpus"
        module.fail_json(msg=err)
    else:
        output = str(result[1])
        try:
            for line in output.split('\n'):
                if line and '#' not in line:
                    cpu_info = line.split(',')
                    node = int(cpu_info[0])
                    thread = int(cpu_info[1])
                    if node in dict_cpus:
                        if thread not in dict_cpus[node]:
                            dict_cpus[node].append(thread)
                    else:
                        dict_cpus[node] = [thread]
        except (IndexError, ValueError):
            err = "Unable to determine NUMA cpus"
            module.fail_json(msg=err)
    return dict_cpus


def check_cpus_aligned_with_dpdk_nics(module, cpus, numa_node, dpdk_nics_numa_info):
    """Checks cpus aligned with NUMA with DPDK NIC's."""

    result = dict(
        changed=False,
        valid_cpus=False,
        message=''
    )
    nodes = []
    valid_numa = False
    invalid_cpus = []
    nodes_cpus = get_nodes_cpus_info(module)
    for dpdk_nics_numa in dpdk_nics_numa_info:
        if (dpdk_nics_numa['numa_node'] == numa_node):
            valid_numa = True
            break
    if not valid_numa:
        err = "NFV instance is not aligned with DPDK NIC's NUMA."
        module.fail_json(msg=err)
    for cpu in cpus.split(','):
        if not int(cpu) in nodes_cpus[numa_node]:
            invalid_cpus.append(cpu)
    if invalid_cpus:
        err = "CPU's are not aligned with DPDK NIC's NUMA, Invalid CPU's: "+','.join(invalid_cpus)
        result['message'] = err
        result['valid_cpus'] = False
        module.fail_json(msg=err)
    else:
        result['message'] = "CPU's configured correctly: " + cpus
        result['valid_cpus'] = True
        module.exit_json(**result)


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

    check_cpus_aligned_with_dpdk_nics(module,
                                      module.params.get('cpus'),
                                      module.params.get('numa_node'),
                                      module.params.get('dpdk_nics_numa_info'))


if __name__ == '__main__':
    main()
