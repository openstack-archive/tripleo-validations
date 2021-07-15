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
"""convert_range_to_numbers_list module
Used by the `check_nfv_ovsdpdk_zero_packet_loss` role.
"""

from ansible.module_utils.basic import AnsibleModule
from yaml import safe_load as yaml_safe_load

DOCUMENTATION = '''
---
module: Converts the CPU's range list into numbers list
short_description: Converts the CPU's range list into numbers list
description:
    - Converts CPU's range list into numbers list
    - Owned by the DFG:NFV Integration
options:
    range_list:
        required: true
        description:
           - The cpus range list
        type: str
author: "Jaganathan Palanisamy"
'''

EXAMPLES = '''
# Call this module from TripleO Ansible Validations

- name: Converts CPU's range list into numbers list
  convert_range_to_numbers_list:
    range_list: "12-14,17"
  register: numbers_list
'''


def convert_range_to_numbers_list(module, range_list):
    """Converts range list into number list
    here input parameter and return value as list
    example: "12-14,17" into [12, 13, 14, 17]
    """

    num_list = []
    exclude_num_list = []
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
    number_list = [num for num in num_list if num not in exclude_num_list]
    return number_list


def get_number_list(module, range_list):
    """Checks PMD threads used in any other process or not."""

    result = dict(
        number_list=[]
    )
    result['number_list'] = convert_range_to_numbers_list(module, range_list)
    module.exit_json(**result)


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

    get_number_list(module, module.params.get('range_list'))


if __name__ == '__main__':
    main()
