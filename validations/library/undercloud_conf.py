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

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

from os import path

from ansible.module_utils.basic import *  # noqa

DOCUMENTATION = '''
---
module: undercloud_conf
short_description: Read undercloud config file
description:
    - Add contents of the undercloud config file to ansible_facts.
options:
    undercloud_conf_path:
        required: true
        description:
           - Path to the undercloud_conf file
        type: str
    ignore_missing:
        required: false
        description:
           - Ignore missing file
        type: bool
author: "Martin Andre (@mandre)"
'''

EXAMPLES = '''
- hosts: undercloud
  tasks:
  - name: Gather undercloud.conf values
    become: true
    undercloud_conf:
      undercloud_conf_path=/home/stack/undercloud.conf
      ignore_missing=true
'''


def check_arguments(undercloud_conf_path, ignore_missing):
    '''Validate format of arguments

    return: (True, errors) if file can be opened
            (False, errors) if ignore_missing or check failed
    '''

    errors = []

    if path.exists(undercloud_conf_path) and path.isfile(undercloud_conf_path):
        return (True, errors)
    else:
        if not ignore_missing:
            errors.append('Could not open the undercloud.conf file at {}'
                          .format(undercloud_conf_path))
        return (False, errors)


def get_result(undercloud_conf_path):
    '''Get result from undercloud file'''

    result = {}
    errors = []

    try:
        config = ConfigParser.SafeConfigParser()
        config.read(undercloud_conf_path)
    except ConfigParser.MissingSectionHeaderError:
        return (['File contains no section headers.'], {})
    except ConfigParser.ParsingError:
        return (['File contains parsing errors.'], {})

    sections = ['DEFAULT'] + config.sections()
    result = dict(((section, dict(config.items(section)))
                   for section in sections))
    return (errors, result)


def main():
    module = AnsibleModule(argument_spec=dict(
        undercloud_conf_path=dict(required=True, type='str'),
        ignore_missing=dict(type='bool'),
    ))

    undercloud_conf_path = module.params.get('undercloud_conf_path')
    ignore_missing = module.params.get('ignore_missing')

    # Check arguments
    file_exists, errors = check_arguments(undercloud_conf_path, ignore_missing)

    if errors:
        module.fail_json(msg='\n'.join(errors))
    elif file_exists:
        # Get result
        errors, result = get_result(undercloud_conf_path)

        if errors:
            module.fail_json(msg='\n'.join(errors))
        else:
            module.exit_json(changed=False,
                             ansible_facts={u'undercloud_conf': result})
    else:
        module.exit_json(changed=False,
                         ansible_facts={u'undercloud_conf': {'DEFAULT': {}}})

if __name__ == '__main__':
    main()
