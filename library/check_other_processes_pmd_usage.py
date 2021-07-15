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
"""check_other_processes_pmd_usage module
Used by the `check_nfv_ovsdpdk_zero_packet_loss` role.
"""

from ansible.module_utils.basic import AnsibleModule
from yaml import safe_load as yaml_safe_load

DOCUMENTATION = '''
---
module: Check OVS DPDK PMD threads used by other processes or not
short_description: Run PMD threads used by other processes or not check
description:
    - Run PMD threads used by other processes or not check
    - Owned by the DFG:NFV Integration
options:
    pmd_cpus:
        required: true
        description:
           - The pmd cpus list
        type: list
    exclude_processes_pid:
        required: false
        description:
           - The processes pid list which need to be excluded.
           - This option is optional.
        default: []
        type: list

author: "Jaganathan Palanisamy"
'''

EXAMPLES = '''
# Call this module from TripleO Ansible Validations

- name: Run PMD threads used by other processes or not check
  become: true
  check_other_processes_pmd_usage:
    pmd_cpus: [6, 7, 9, 11]
  register: pmd_interrupts

- name: Run PMD threads used by other processes or not with exclude processes
  become: true
  check_other_processes_pmd_usage:
    pmd_cpus: [6, 7, 9, 11]
    exclude_processes_pid: ['24', '26']
  register: pmd_interrupts
'''


def check_current_process_pmd_usage(module, pmd_cpus, process_id, range_list):
    """Check pmd usage in current process cpus range list."""

    messages = []
    num_list = []
    exclude_num_list = []
    threads_used = []
    try:
        for val in range_list.split(','):
            val = val.strip(' ')
            if '^' in val:
                exclude_num_list.append(int(val[1:]))
            elif '-' in val:
                split_list = val.split("-")
                range_min = int(split_list[0])
                range_max = int(split_list[1])
                num_list.extend(range(range_min, (range_max + 1)))
            else:
                num_list.append(int(val))
    except ValueError as exc:
        err = ("Invalid number in input param "
               "'range_list': %s" % exc)
        module.fail_json(msg=err)
    # here, num_list is a list of integers
    threads_list = [str(num) for num in num_list if num not in exclude_num_list]
    for thread in threads_list:
        if thread in pmd_cpus:
            if threads_used:
                threads_used.append(thread)
            else:
                threads_used = [thread]
    if threads_used:
        messages.append("pmd threads: " + ','.join(threads_used) + " used in process: " + process_id)
    return list(messages)


def check_other_processes_pmd_usage(module, pmd_cpus, exclude_processes_pid):
    """Checks PMD threads used in any other process or not"""

    output = dict(
        pmd_interrupts=False,
        messages=[]
    )
    messages = []
    threads_used = {}
    current_processes = []

    # Gets all the processes and corresponding threads usage
    # except processes mentioned in exclude_processes_pid list
    # processes pid and threads information
    cmd = ("find -L /proc/[0-9]*/exe ! -type l | cut -d / -f3 | "
           "xargs -l -i sh -c 'ps -p {} -o comm=; taskset -acp {}' | "
           "grep -vE '" + '|'.join(exclude_processes_pid) + "' | "
           "awk '{printf \"%s %s\\n\", $2, $6}'")
    result = module.run_command(cmd, use_unsafe_shell=True)
    if (not result or (result[0] != 0) or not (str(result[1]).strip(' '))):
        err = "Unable to determine current processes"
        module.fail_json(msg=err)
    else:
        current_processes = str(result[1]).split('\n')

    pmd_threads_processes = []
    # Gets processes associated to PMD and corresponding threads usage
    # proceses pid and threads information
    cmd = ("ps -T -o spid,comm -p $(pidof ovs-vswitchd) |grep '\<pmd' | "
           "while read spid name; do echo $(taskset -p -c $spid) | "
           "awk '{printf \"%s %s\\n\", $2, $6}'; done")
    result = module.run_command(cmd, use_unsafe_shell=True)
    if (not result or (result[0] != 0) or not (str(result[1]).strip(' '))):
        err = "Unable to determine PMD threads processes"
        module.fail_json(msg=err)
    else:
        pmd_threads_processes = str(result[1]).split('\n')

    for process in current_processes:
        process = process.strip(' ')
        if process and process not in pmd_threads_processes:
            process_params = process.split(' ')
            if len(process_params) == 2:
                process_id = process_params[0].strip("'s")
                messages.extend(
                    check_current_process_pmd_usage(module, pmd_cpus, process_id, process_params[1]))
    output['messages'] = messages
    if messages:
        output['pmd_interrupts'] = True
    module.exit_json(**output)


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

    check_other_processes_pmd_usage(module,
                                    module.params.get('pmd_cpus'),
                                    module.params.get('exclude_processes_pid'))
if __name__ == '__main__':
    main()
