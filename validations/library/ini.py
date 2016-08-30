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


def main():
    module = AnsibleModule(argument_spec=dict(
        path=dict(required=True, type='str'),
        section=dict(required=True, type='str'),
        key=dict(required=True, type='str'),
    ))

    ini_file_path = module.params.get('path')

    if path.exists(ini_file_path) and path.isfile(ini_file_path):
        config = ConfigParser.SafeConfigParser()
        config.read(ini_file_path)

        try:
            value = config.get(module.params.get('section'),
                               module.params.get('key'))
        except ConfigParser.Error as e:
            module.fail_json(msg=e.message)

        module.exit_json(changed=False, value=value)
    else:
        module.fail_json(msg="Could not open the ini file: '{}'"
                         .format(ini_file_path))


if __name__ == '__main__':
    main()
