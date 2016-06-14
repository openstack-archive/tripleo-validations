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

import ConfigParser
from os import path

from ansible.module_utils.basic import *  # noqa


def main():
    module = AnsibleModule(argument_spec=dict(
        undercloud_conf_path=dict(required=True, type='str'),
    ))

    undercloud_conf_path = module.params.get('undercloud_conf_path')

    if path.exists(undercloud_conf_path) and path.isfile(undercloud_conf_path):
        config = ConfigParser.SafeConfigParser()
        config.read(undercloud_conf_path)

        sections = ['DEFAULT'] + config.sections()
        result = dict(((section, dict(config.items(section)))
                       for section in sections))

        module.exit_json(changed=False,
                         ansible_facts={u'undercloud_conf': result})
    else:
        module.fail_json(msg="Could not open the undercloud.conf file at '%s'"
                         % undercloud_conf_path)


if __name__ == '__main__':
    main()
