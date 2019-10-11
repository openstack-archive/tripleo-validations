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

from ansible.module_utils.basic import AnsibleModule
from yaml import safe_load as yaml_safe_load

DOCUMENTATION = '''
---
module: OVS DPDK PMD CPU's check
short_description: Run PMD CPU's from all the NUMA nodes check
description:
    - Run PMD CPU's from all the NUMA nodes check
options:
    pmd_cpu_mask:
        required: true
        description:
           - The pmd cpu mask value
        type: str
author: "Jaganathan Palanisamy"
'''

EXAMPLES = '''
- hosts: ComputeOvsDpdk
  vars:
    pmd_cpu_mask: "1010010000000001"
  tasks:
  - name: Run PMD CPU's check
    become: true
    ovs_dpdk_pmd_cpus_check: pmd_cpu_mask={{ pmad_cpu_mask }}
'''


def get_cpus_list_from_mask_value(mask_val):
    """Gets CPU's list from the mask value

    :return: comma separated CPU's list
    """
    mask_val = mask_val.strip('\\"')
    cpus_list = []
    int_mask_val = int(mask_val, 16)
    bin_mask_val = bin(int_mask_val)
    bin_mask_val = str(bin_mask_val).replace('0b', '')
    rev_bin_mask_val = bin_mask_val[::-1]
    thread = 0
    for bin_val in rev_bin_mask_val:
        if bin_val == '1':
            cpus_list.append(thread)
        thread += 1
    return ','.join([str(cpu) for cpu in cpus_list])


# Gets the distinct numa nodes, physical and logical cpus info
# for all numa nodes.
def get_nodes_cores_info(module):
    dict_cpus = {}
    numa_nodes = []
    cmd = "sudo lscpu -p=NODE,CORE,CPU"
    result = module.run_command(cmd)
    if (not result or (result[0] != 0) or not (str(result[1]).strip(' '))):
        err = "Unable to determine physical and logical cpus."
        module.fail_json(msg=err)
    else:
        for line in str(result[1]).split('\n'):
            if (line.strip(' ') and not line.strip(' ').startswith('#')):
                cpu_info = line.strip(' ').split(',')
                try:
                    node = int(cpu_info[0])
                    cpu = int(cpu_info[1])
                    thread = int(cpu_info[2])
                    if node not in numa_nodes:
                        numa_nodes.append(node)
                    # CPU and NUMA node together forms a unique value,
                    # as cpu is specific to a NUMA node
                    # NUMA node id and cpu id tuple is used for unique key
                    key = node, cpu
                    if key in dict_cpus:
                        if thread not in dict_cpus[key]['thread_siblings']:
                            dict_cpus[key]['thread_siblings'].append(thread)
                    else:
                        cpu_item = {}
                        cpu_item['thread_siblings'] = [thread]
                        cpu_item['cpu'] = cpu
                        cpu_item['numa_node'] = node
                        dict_cpus[key] = cpu_item
                except (IndexError, ValueError):
                    err = "Unable to determine physical and logical cpus."
                    module.fail_json(msg=err)
    return (numa_nodes, list(dict_cpus.values()))


def validate_pmd_cpus(module, pmd_cpu_mask):
    pmd_cpus = get_cpus_list_from_mask_value(pmd_cpu_mask)
    pmd_cpu_list = pmd_cpus.split(',')
    cpus = []
    numa_nodes = []
    numa_nodes, cpus = get_nodes_cores_info(module)
    valid_numa_nodes = {}
    for numa_node in numa_nodes:
        valid_numa_nodes[str(numa_node)] = False
        for cpu in cpus:
            if cpu['numa_node'] == numa_node:
                if True in [int(pmd_cpu) in cpu['thread_siblings']
                            for pmd_cpu in pmd_cpu_list]:
                    valid_numa_nodes[str(numa_node)] = True
    invalid_numa_nodes = [node for node, val in valid_numa_nodes.items()
                          if not val]
    if invalid_numa_nodes:
        failed_nodes = ','.join(invalid_numa_nodes)
        err = ("Invalid PMD CPU's, cpu is not used from "
               "NUMA node(s): %(node)s." % {'node': failed_nodes})
        module.fail_json(msg=err)
    else:
        module.exit_json(msg="PMD CPU's configured correctly.")


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

    validate_pmd_cpus(module,
                      module.params.get('pmd_cpu_mask'))


if __name__ == '__main__':
    main()
