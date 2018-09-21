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

from ansible.module_utils.basic import AnsibleModule  # noqa

DOCUMENTATION = '''
---
module: node_disks
short_description: Check disks, flavors and root device hints
description:
    - Check if each node has a root device hint set if there is more
    than one disk and compare flavors to disk sizes.
options:
    nodes:
        required: true
        description:
            - A list of nodes
        type: list
    flavors:
        required: true
        description:
            - A list of flavors
        type: list
    introspection_data:
        required: true
        description:
            - Introspection data for all nodes
        type: list

author: "Florian Fuchs <flfuchs@redhat.com>"
'''

EXAMPLES = '''
- hosts: undercloud
  tasks:
    - name: Check node disks
      node_disks:
        nodes: "{{ lookup('ironic_nodes') }}"
        flavors: "{{ lookup('nova_flavors') }}"
        introspection_data: "{{ lookup('introspection_data',
            auth_url=auth_url.value, password=password.value) }}"
'''


IGNORE_BYTE_MAX = 4294967296

ONE_DISK_TOO_SMALL_ERROR = """\
The node {} only has one disk and it's too small for the "{}" flavor"""

NO_RDH_SMALLEST_DISK_TOO_SMALL_ERROR = (
    '{} has more than one disk available for deployment and no '
    'root device hints set. The disk that will be used is too small '
    'for the flavor with the largest disk requirement ("{}").')


def _get_minimum_disk_size(flavors):
    min_gb = 0
    name = 'n.a.'
    for key, val in flavors.items():
        disk_gb = val['disk']
        if disk_gb > min_gb:
            min_gb = disk_gb
            name = key
    # convert GB to bytes to compare to introspection data
    return name, min_gb * 1073741824


def _get_smallest_disk(disks):
    smallest = disks[0]
    for disk in disks[1:]:
        if disk['size'] < smallest['size']:
            smallest = disk
    return smallest


def _has_root_device_hints(node_name, node_data):
    rdh = node_data.get(
        node_name, {}).get('properties', {}).get('root_device')
    return rdh is not None


def validate_node_disks(nodes, flavors, introspection_data):
    """Validate root device hints using introspection data.

      :param nodes: Ironic nodes
      :param introspection_data: Introspection data for all nodes
      :returns warnings: List of warning messages
               errors: List of error messages
    """
    errors = []
    warnings = []
    # Get the name of the flavor with the largest disk requirement,
    # which defines the minimum disk size.
    max_disk_flavor, min_disk_size = _get_minimum_disk_size(flavors)

    for node, content in introspection_data.items():
        disks = content.get('inventory', {}).get('disks')
        valid_disks = [disk for disk in disks
                       if disk['size'] > IGNORE_BYTE_MAX]

        root_device_hints = _has_root_device_hints(node, nodes)
        smallest_disk = _get_smallest_disk(valid_disks)

        if len(valid_disks) == 1:
            if smallest_disk.get('size', 0) < min_disk_size:
                errors.append(ONE_DISK_TOO_SMALL_ERROR.format(
                              node, max_disk_flavor))
        elif not root_device_hints and len(valid_disks) > 1:
            if smallest_disk.get('size', 0) < min_disk_size:
                errors.append(NO_RDH_SMALLEST_DISK_TOO_SMALL_ERROR.format(
                              node, max_disk_flavor))
            else:
                warnings.append('{} has more than one disk available for '
                                'deployment'.format(node))

    return errors, warnings


def main():
    module = AnsibleModule(argument_spec=dict(
        nodes=dict(required=True, type='list'),
        flavors=dict(required=True, type='dict'),
        introspection_data=dict(required=True, type='list')
    ))

    nodes = {node['name']: node for node in module.params.get('nodes')}
    flavors = module.params.get('flavors')
    introspection_data = {name: content for (name, content) in
                          module.params.get('introspection_data')}

    errors, warnings = validate_node_disks(nodes,
                                           flavors,
                                           introspection_data)

    if errors:
        module.fail_json(msg="\n".join(errors))
    elif warnings:
        module.exit_json(warnings="\n".join(warnings))
    else:
        module.exit_json(msg="Root device hints are either set or not "
                             "necessary.")


if __name__ == '__main__':
    main()
