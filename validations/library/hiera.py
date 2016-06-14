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

import subprocess

from ansible.module_utils.basic import *  # noqa


def main():
    module = AnsibleModule(argument_spec=dict(
        name=dict(required=True, type='str'),
    ))

    name = module.params.get('name')

    cmd = ['/usr/bin/hiera', name]
    result = subprocess.check_output(cmd).rstrip()

    if result == 'nil':
        module.fail_json(msg="Failed to retrieve hiera data for {}"
                         .format(name))

    module.exit_json(changed=False,
                     ansible_facts={name: result})


if __name__ == '__main__':
    main()
