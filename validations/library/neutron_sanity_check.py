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

import subprocess

from ansible.module_utils.basic import AnsibleModule
from os import path

DOCUMENTATION = '''
---
module: neutron_sanity_check
short_description: Run neutron-sanity-check on a number of config files
description:
    - Run neutron-sanity-check on a number of config files
options:
    configs:
        required: true
        description:
           - The config file paths
        type: list
author: "Tomas Sedovic"
'''

EXAMPLES = '''
- hosts: webservers
  vars:
    configs:
      - /etc/neutron/neutron.conf
      - /usr/share/neutron/neutron-dist.conf
      - /etc/neutron/metadata_agent.ini
      - /etc/neutron/metering_agent.ini
      - /etc/neutron/dhcp_agent.ini
  tasks:
  - name: Run neutron-sanity-check
    become: true
    neutron_sanity_check: configs={{ configs }}
'''


def main():
    module = AnsibleModule(argument_spec=dict(
        configs=dict(required=True, type='list'),
    ))

    # Input configurations as a list
    i_config = module.params.get('configs')

    # Arguments as a list contianing only existing files/dirs
    o_config = []

    # Create arguments
    o_config.append('neutron-sanity-check')
    o_config.append("--nodnsmasq_version")

    for c in i_config:
        if path.isfile(c):
            o_config.append('--config-file')
            o_config.append(c)
        elif path.isdir(c):
            o_config.append('--config-dir')
            o_config.append(c)

    # Execute neutron-sanity-check, fetch stdout, stderr
    # neutron-sanity-check --nodnsmasq_version $ARGS
    process = subprocess.Popen(o_config, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Filter warnings and errors - neutron-sanity-checks puts it all to stderr
    output = stderr.split('\n')
    o_warnings = []
    o_errors = ""
    for line in output:
        if 'WARNING' in line:
            o_warnings.append(line.split('WARNING')[1])
        elif 'ERROR' in line:
            o_errors += line.split('ERROR')[1] + "\n"

    # Based on stdout and stderr, exit module
    if o_errors:
        module.fail_json(msg=o_errors, warnings=o_warnings, changed=True)
    else:
        module.exit_json(warnings=o_warnings, changed=True)


if __name__ == '__main__':
    main()
