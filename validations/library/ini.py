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

# Ansible module to read a value from an Ini file.
# Usage:
#     - ini: path=/path/to/file.ini section=default key=something
#       register: my_ini
#
# This will read the `path/to/file.ini` file and read the `Hello!` value under:
#     [default]
#     something = Hello!
#
# You can register the result and use it later with `{{ my_ini.value }}`

import ConfigParser
from os import path

from ansible.module_utils.basic import *  # NOQA

DOCUMENTATION = '''
---
module: ini
short_description: Get data from an ini file
description:
    - Get data from an ini file
options:
    path:
        required: true
        description:
            - File path
        type: str
    section:
        required: true
        description:
            - Section to look up
        type: str
    key:
        required: true
        description:
            - Section key to look up
        type: str
    ignore_missing_file:
        required: false
        description:
            - Flag if a missing file should be ignored
        type: bool
author: "Tomas Sedovic"
'''

EXAMPLES = '''
- hosts: webservers
  tasks:
    - name: Lookup bar value
      ini: path=config.ini section=foo key=bar ignore_missing_file=True
'''


def main():
    module = AnsibleModule(argument_spec=dict(
        path=dict(required=True, type='str'),
        section=dict(required=True, type='str'),
        key=dict(required=True, type='str'),
        ignore_missing_file=dict(required=False, type='bool'),
    ))

    ini_file_path = module.params.get('path')

    if path.exists(ini_file_path) and path.isfile(ini_file_path):
        config = ConfigParser.SafeConfigParser()
        try:
            config.read(ini_file_path)
        except Exception:
            module.fail_json(msg="The file '{}' is not in a valid INI format."
                             .format(ini_file_path))

        section = module.params.get('section')
        key = module.params.get('key')
        try:
            value = config.get(section, key)
            msg = ("The key '{}' under the section '{}' in file {} "
                   "has the value: '{}'"
                   .format(key, section, ini_file_path, value))
            module.exit_json(msg=msg, changed=False, value=value)
        except ConfigParser.Error:
            msg = ("There is no key '{}' under the section '{}' in file {}."
                   .format(key, section, ini_file_path))
            module.exit_json(msg=msg, changed=False, value=None)

    else:
        missing_file_message = "Could not open the ini file: '{}'".format(
            ini_file_path)
        if module.params.get('ignore_missing_file'):
            module.exit_json(msg=missing_file_message, changed=False,
                             value=None)
        else:
            module.fail_json(msg=missing_file_message)


if __name__ == '__main__':
    main()
