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

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

from enum import Enum
import os

from ansible.module_utils.basic import AnsibleModule


# Possible return values
class ReturnValue(Enum):
    OK = 0
    INVALID_FORMAT = 1
    KEY_NOT_FOUND = 2


def check_file(path, ignore_missing):
    '''Validate entered path'''

    if not (os.path.exists(path) and os.path.isfile(path)):
        return "Could not open the ini file: '{}'".format(path)
    else:
        return ''


def get_result(path, section, key):
    '''Get value based on section and key'''

    msg = ''
    value = None
    config = ConfigParser.SafeConfigParser()

    try:
        config.read(path)
    except Exception:
        msg = "The file '{}' is not in a valid INI format.".format(path)
        ret = ReturnValue.INVALID_FORMAT
        return (ret, msg, value)

    try:
        value = config.get(section, key)
        msg = ("The key '{}' under the section '{}' in file {} "
               "has the value: '{}'").format(key, section, path, value)
        ret = ReturnValue.OK
        return (ret, msg, value)
    except ConfigParser.Error:
        value = None
        msg = "There is no key '{}' under the section '{}' in file {}.".format(
              key, section, path)
        ret = ReturnValue.KEY_NOT_FOUND
        return (ret, msg, value)

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
    ignore_missing = module.params.get('ignore_missing_file')

    # Check that file exists
    msg = check_file(ini_file_path, ignore_missing)

    if msg != '':
        # Opening file failed
        if ignore_missing:
            module.exit_json(msg=msg, changed=False, value=None)
        else:
            module.fail_json(msg=msg)
    else:
        # Try to parse the result from ini file
        section = module.params.get('section')
        key = module.params.get('key')

        ret, msg, value = get_result(ini_file_path, section, key)

        if ret == ReturnValue.INVALID_FORMAT:
            module.fail_json(msg=msg)
        elif ret == ReturnValue.KEY_NOT_FOUND:
            module.exit_json(msg=msg, changed=False, value=None)
        elif ret == ReturnValue.OK:
            module.exit_json(msg=msg, changed=False, value=value)


if __name__ == '__main__':
    main()
