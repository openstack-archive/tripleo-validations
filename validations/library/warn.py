#!/usr/bin/env python
# Copyright 2017 Red Hat, Inc.
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

from ansible.module_utils.basic import *  # noqa

DOCUMENTATION = '''
---
module: warn
short_description: Add warning to playbook output
description:
    - Add warning to playbook output
options:
    msg:
        required: true
        description:
           - The warning text
        type: str
author: "Martin Andre (@mandre)"
'''

EXAMPLES = '''
- hosts: webservers
  tasks:
  - name: Output warning message
    warn: msg="Warning!"
'''


def main():
    module = AnsibleModule(argument_spec=dict(
        msg=dict(required=True, type='str'),
    ))

    msg = module.params.get('msg')

    module.exit_json(changed=False,
                     warnings=[msg])


if __name__ == '__main__':
    main()
