# Copyright 2019 Red Hat, Inc.
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
from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
module: mocked podman_container_info
author:
    - David Vallee Delisle (@dvd)
short_description: Mocking gather facts about containers using podman
description:
    - Mocking gather facts about containers using podman
'''

EXAMPLES = r"""
- name: Gather facts for all containers
  podman_container_info:
"""

RETURN = r"""
containers:
    description: Facts from all or specificed containers
    returned: always
    type: list
    elements: dict
    sample: {
         "Id": "21d8b432eaec1b4eac2a21a78de524bdbb2f074d4ea43d3605b2b072ffe21878",
         "State": {
           "Status": "running",
           "Running": true,
         },
         "Image": "0ece6dfb3015c221c8ad6d364dea7884ae3e24becd60e94b80d5361f4ed78f47",
         "ImageName": "undercloud-0.ctlplane.redhat.local:8787/rh-osbs/rhosp16-openstack-nova-compute:16.1_20210430.1",
         "Name": "nova_compute",
         "Mounts": [],
      }
"""

from ansible.module_utils.basic import AnsibleModule  # noqa: F402
from yaml import safe_load as yaml_safe_load


def main():
    module = AnsibleModule({}, supports_check_mode=True)
    sample = yaml_safe_load(RETURN)['containers']['sample']
    with open('/test.config.yml', 'r') as yaml_config:
        test_config = yaml_safe_load(yaml_config)
    config_folder = test_config.get('config_folder')
    sample['Name'] = test_config.get('service_name')
    sample['State']['Running'] = bool(test_config.get('service_running', True))
    sample['Mounts'].append({'Type': 'bind', 'Source':  config_folder})
    module.exit_json(**{
        "changed": False,
        "containers": [sample],
    })

if __name__ == '__main__':
    main()
