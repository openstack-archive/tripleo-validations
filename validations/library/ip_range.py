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

import netaddr

from ansible.module_utils.basic import *  # NOQA

DOCUMENTATION = '''
---
module: ip_range
short_description: Check the size of an IP range
description:
    - Check if the size of an IP range against a minimum value.
options:
    start:
        required: true
        description:
            - Start IP
        type: str
    end:
        required: true
        description:
            - End IP
        type: str
    min_size:
        required: true
        description:
            - Minum size of the range
        type: int
author: "Tomas Sedovic"
'''

EXAMPLES = '''
- hosts: webservers
  tasks:
    - name: Check the IP range
      ip_range:
        start: 192.0.2.5
        end: 192.0.2.24
        min_size: 15
'''


def check_arguments(start, end, min_size):
    '''Validate format of arguments'''

    errors = []

    # Check format of arguments
    try:
        startIP = netaddr.IPAddress(start)
    except netaddr.core.AddrFormatError:
        errors.append('Argument start ({}) must be an IP'.format(start))

    try:
        endIP = netaddr.IPAddress(end)
    except netaddr.core.AddrFormatError:
        errors.append('Argument end ({}) must be an IP'.format(end))

    if (not errors) and (startIP.version != endIP.version):
        errors.append('Arguments start, end must share the same IP version')

    if min_size < 0:
        errors.append('Argument min_size({}) must be greater than 0'
                      .format(min_size))

    return errors


def check_IP_range(start, end, min_size):
    '''Compare IP range with minimum size'''

    warnings = []
    iprange = netaddr.IPRange(start, end)

    if len(iprange) < min_size:
        warnings = [
            'The IP range {} - {} contains {} addresses.'.format(
                start, end, len(iprange)),
            'This might not be enough for the deployment or later scaling.'
        ]

    return warnings


def main():
    module = AnsibleModule(argument_spec=dict(
        start=dict(required=True, type='str'),
        end=dict(required=True, type='str'),
        min_size=dict(required=True, type='int'),
    ))

    start = module.params.get('start')
    end = module.params.get('end')
    min_size = module.params.get('min_size')

    # Check arguments
    errors = check_arguments(start, end, min_size)
    if errors:
        module.fail_json(msg='\n'.join(errors))
    else:
        # Check IP range
        warnings = check_IP_range(start, end, min_size)

        if warnings:
            module.exit_json(changed=True, warnings=warnings)
        else:
            module.exit_json(msg='success')


if __name__ == '__main__':
    main()
