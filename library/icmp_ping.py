#!/usr/bin/env python
# Copyright 2016 Red Hat, Inc.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""icmp_ping module
Used by `node-health` and `check-network-gateway` roles.
"""
from ansible.module_utils.basic import AnsibleModule
from yaml import safe_load as yaml_safe_load

DOCUMENTATION = '''
---
module: icmp_ping
short_description: ICMP ping remote hosts
requirements: [ ping ]
description:
    - Check host connectivity with ICMP ping.
    - Used by `node-health` and `check-network-gateway` roles.
    - Owned by the DFG:DF and DFG:Networking
options:
    host:
        required: true
        description:
            - IP address or hostname of host to ping
        type: str
author: "Martin Andre (@mandre)"
'''

EXAMPLES = '''
# Ping host:
- icmp: name=somegroup state=present
- hosts: webservers
  tasks:
    - name: Check Internet connectivity
      ping: host="www.ansible.com"
'''


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

    host = module.params.pop('host')
    result = module.run_command('ping -c 1 {}'.format(host))
    failed = (result[0] != 0)
    msg = result[1] if result[1] else result[2]

    module.exit_json(changed=False, failed=failed, msg=msg)


if __name__ == '__main__':
    main()
