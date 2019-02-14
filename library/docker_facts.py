#!/usr/bin/env python
# Copyright 2018 Red Hat, Inc.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import six
six.add_metaclass(type)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: docker_facts
version_added: '2.6'
short_description: Gather list of volumes, images, containers
notes:
    - When specifying mulitple filters, only assets matching B(all) filters
      will be returned.
description:
    - Gather a list of volumes, images, and containers on a running system
    - Return both filtered and unfiltered lists of volumes, images,
      and containers.
options:
    image_filter:
        description:
            - List of k=v pairs to use as a filter for images.
        type: list
        required: false
    volume_filter:
        description:
            - List of k=v pairs to use as a filter for volumes.
        type: list
        required: false
    container_filter:
        description:
            - List of k=v pairs to use as a filter for containers.
        type: list
        required: false

"""

EXAMPLES = """
- name: Gather Docker facts
  docker_facts:

- name: Gather filtered Docker facts
  docker_facts:
    image_filter:
      - dangling=true
    volume_filter:
      - dangling=true
    container_filter:
      - status=exited
      - status=dead

- name: Remove containers that matched filters
  docker_container:
    name: "{{ item }}"
    state: absent
  loop: "{{ docker.containers_filtered | map(attribute='id') | list }}"

"""

RETURN = """
docker:
  description: >
    Lists of container, volume, and image UUIDs,
    both filtered and unfiltered.
  returned: always
  type: complex
  contains:
    containers:
        description: List of dictionaries of container name, state, and ID
        returned: always
        type: complex
    containers_filtered:
        description: >
            List of dictionaries of container name, state, and ID
            that matched the filter(s)
        returned: always
        type: complex
    images:
        description: List of image UUIDs
        returned: always
        type: list
    images_filtered:
        description: List of UUIDs that matched the filter(s)
        returned: always
        type: list
    volumes:
        description: List of volume UUIDs
        returned: always
        type: list
    volumes_filtered:
        description: List of UUIDs that matched the filter(s)
        returned: always
        type: list
"""

import itertools

from ansible.module_utils.basic import AnsibleModule

DOCKER_SUBCOMMAND_LOOKUP = [
    ('images', 'images', '-q'),
    ('volumes', 'volume ls', '-q'),
    ('containers', 'ps -a', '--format {{.Names}}##{{.ID}}##{{.Status}}')
]


def run_docker_command(
        module,
        docker_bin,
        sub_command=[],
        opts='-q',
        filters=[]):

    for item in docker_bin, sub_command, opts, filters:
        if not isinstance(item, list):
            item = item.split('\n')

    if not isinstance(docker_bin, list):
        docker_bin = docker_bin.split()

    if not isinstance(sub_command, list):
        sub_command = sub_command.split()

    if not isinstance(opts, list):
        opts = opts.split()

    if not isinstance(filters, list):
        filters = filters.split()

    filters = ['-f ' + i for i in filters]
    command = list(itertools.chain(docker_bin, sub_command, opts, filters))
    rc, out, err = module.run_command(command)

    if rc != 0:
        module.fail_json(
            msg='Error running command {}.\n\n \
                 Original error:\n\n{}'.format(command, err))

    if out == '':
        out = []
    else:
        out = out.strip().split('\n')

    return rc, out, err


def main():
    module = AnsibleModule(
        argument_spec=dict(
            image_filter=dict(type='list', default=[]),
            volume_filter=dict(type='list', default=[]),
            container_filter=dict(type='list', default=[]),
        ),

        supports_check_mode=True
    )

    docker_bin = [module.get_bin_path('docker')]

    docker_facts = {}

    for item in DOCKER_SUBCOMMAND_LOOKUP:
        docker_facts[item[0]] = []
        docker_facts[item[0] + '_filtered'] = []

    if docker_bin[0]:

        docker_facts[item[0]] = []

        # Run each Docker command
        for item in DOCKER_SUBCOMMAND_LOOKUP:
            rc, out, err = run_docker_command(
                module,
                docker_bin,
                sub_command=item[1],
                opts=item[2])

            # For everything but containers, return just the UIDs
            if item[0] != 'containers':
                docker_facts[item[0]] = out
            elif item[0] == 'containers':

                # For containers, use a custom format to get name, id,
                # and status
                for line in out:
                    container_name, container_id, container_status = \
                        line.split('##')
                    container_status = container_status.split()[0]
                    docker_facts[item[0]].append({
                        'name': container_name,
                        'id': container_id,
                        'status': container_status
                    })

            # Get filtered facts
            rc, out, err = run_docker_command(
                module,
                docker_bin,
                sub_command=item[1],
                opts=item[2],
                filters=module.params[item[0].rstrip('s') + '_filter']
            )

            if item[0] != 'containers':
                docker_facts[item[0] + '_filtered'] = out
            elif item[0] == 'containers':

                for line in out:
                    container_name, container_id, container_status = \
                        line.split('##')
                    container_status = container_status.split()[0]
                    docker_facts[item[0] + '_filtered'].append({
                        'name': container_name,
                        'id': container_id,
                        'status': container_status
                    })

    results = dict(
        ansible_facts=dict(
            docker=docker_facts
        )
    )

    module.exit_json(**results)


if __name__ == '__main__':
    main()
