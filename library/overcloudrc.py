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

import os.path
import subprocess

DOCUMENTATION = '''
---
module: overcloudrc
short_description: Source the overcloudrc file
description:
    - Source the overcloudrc file
options:
    path:
        required: true
        description:
           - The file path
        type: str
author: "Tomas Sedovic"
'''

EXAMPLES = '''
- hosts: webservers
  tasks:
  - name: Source overcloudrc
    overcloudrc: path=/home/stack/overcloudrc
'''


def main():
    module = AnsibleModule(argument_spec=dict(
        path=dict(required=True, type='str'),
    ))

    overcloudrc_path = os.path.expanduser(module.params.get('path'))

    if not os.path.isfile(overcloudrc_path):
        module.fail_json(
            msg="The overcloudrc file at {} does not exist.".format(
                overcloudrc_path))

    # Use bash to source overcloudrc and print the environment:
    command = ['bash', '-c', 'source ' + overcloudrc_path + ' && env']
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True
    )
    if proc.wait() != 0:
        msg = "Could not source '{}'. Return code: {}.\nSTDERR:\n{}".format(
            overcloudrc_path, proc.returncode, proc.stderr.read())
        module.fail_json(msg=msg)

    facts = {}
    for line in proc.stdout:
        (key, _, value) = line.partition("=")
        if key.startswith("OS_"):
            facts[key] = value.rstrip()

    module.exit_json(changed=False, ansible_facts={'overcloudrc': facts})


if __name__ == '__main__':
    main()
