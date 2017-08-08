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

from os import path

from ansible.module_utils.basic import *  # noqa

DOCUMENTATION = '''
---
module: advanced_format
short_description: Check for advanced disk format
description:
    - Check whether a drive uses advanced format
options:
    drive:
        required: true
        description:
            - drive name
        type: str
author: "Martin Andre (@mandre)"
'''

EXAMPLES = '''
- hosts: webservers
  tasks:
    - name: Detect whether the drive uses Advanced Format
      advanced_format: drive=vda
'''


def read_int(module, file_path):
    '''Read a file and convert its value to int.

    Raise ansible failure otherwise.
    '''
    try:
        with open(file_path) as f:
            file_contents = f.read()
        return int(file_contents)
    except IOError:
        module.fail_json(msg="Cannot open '%s'" % file_path)
    except ValueError:
        module.fail_json(msg="The '%s' file doesn't contain an integer value" %
                         file_path)


def main():
    module = AnsibleModule(argument_spec=dict(
        drive=dict(required=True, type='str')
    ))

    drive = module.params.get('drive')
    queue_path = path.join('/sys/class/block', drive, 'queue')

    physical_block_size_path = path.join(queue_path, 'physical_block_size')
    logical_block_size_path = path.join(queue_path, 'logical_block_size')

    physical_block_size = read_int(module, physical_block_size_path)
    logical_block_size = read_int(module, logical_block_size_path)

    if physical_block_size == logical_block_size:
        module.exit_json(
            changed=False,
            msg="The disk %s probably doesn't use Advance Format." % drive,
        )
    else:
        module.exit_json(
            # NOTE(shadower): we're marking this as `changed`, to make it
            # visually stand out when running via Ansible directly instead of
            # using the API.
            #
            # The API & UI is planned to look for the `warnings` field and
            # display it differently.
            changed=True,
            warnings=["Physical and logical block sizes of drive %s differ "
                      "(%s vs. %s). This can mean the disk uses Advance "
                      "Format." %
                      (drive, physical_block_size, logical_block_size)],
        )


if __name__ == '__main__':
    main()
