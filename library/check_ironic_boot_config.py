#!/usr/bin/env python
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

import collections

from ansible.module_utils.basic import AnsibleModule  # noqa
from oslo_utils import uuidutils
from yaml import safe_load as yaml_safe_load

DOCUMENTATION = '''
---
module: check_ironic_boot_config
short_description:
    - Check that overcloud nodes have the correct associated ramdisk and kernel
      image
description:
    - Each overcloud node needs to have the correct associated ramdisk and
      kernel image according to its architecture and platform. This can be
      validated by making sure that like nodes have associated deploy images
      not exceeding a certain standard of diversity.
options:
    nodes:
        required: true
        description:
            - A list of nodes from Ironic
        type: list

author: Jeremy Freudberg
'''

EXAMPLES = '''
- hosts: undercloud
  tasks:
    - name: Check Ironic boot config
      check_ironic_boot_config:
        nodes: "{{ lookup('ironic_nodes', wantlist=True) }}"
'''


GLANCE = 'Glance'
FILE = 'file-based'


def _too_diverse(mapping_type, node_info, images):
    image_type = "deploy_%s" % node_info[0]
    return (
        "There is more than one {} {} associated to nodes with architecture "
        "{} and platform {}. Probably only one of {} should be associated."
    ).format(mapping_type, image_type, node_info[1], node_info[2], images)


def _invalid_image_entry(image_type_base, image_entry, node_id):
    image_type = "deploy_%s" % image_type_base
    return (
        "The {} associated to node {} is of an invalid form. Could not "
        "determine whether {} refers to a file or Glance image."
    ).format(image_type, node_id, image_entry)


def validate_boot_config(nodes):
    errors = []

    associated_images = {
        GLANCE: collections.defaultdict(set),
        FILE: collections.defaultdict(set)
    }

    for node in nodes:
        arch = node["properties"].get("cpu_arch", None)
        platform = node["extra"].get("tripleo_platform", None)

        for image_type in ['kernel', 'ramdisk']:
            image_entry = (
                node["driver_info"].get("deploy_%s" % image_type, None)
            )
            if uuidutils.is_uuid_like(image_entry):
                mapping = GLANCE
            elif str(image_entry).startswith("file://"):
                mapping = FILE
            # TODO(jfreud): uncomment when Ironic supports empty driver_info
#           elif image_entry is None:
#               continue
            else:
                errors.append(_invalid_image_entry(
                    image_type, image_entry, node["uuid"]))
                continue
            node_info = (image_type, arch, platform)
            associated_images[mapping][node_info].add(image_entry)

    for mapping_type, mapping in associated_images.items():
        for node_info, images in mapping.items():
            if len(images) > 1:
                errors.append(_too_diverse(mapping_type, node_info, images))

    return errors


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

    nodes = module.params.get('nodes')

    errors = validate_boot_config(nodes)

    if errors:
        module.fail_json("".join(errors))
    else:
        module.exit_json()


if __name__ == '__main__':
    main()
