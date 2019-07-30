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

DOCUMENTATION = '''
---
module: check_ironic_boot_config
short_description:
    - Check that overcloud nodes have the correct associated ramdisk and kernel
      image
description:
    - Each overcloud node needs to have the correct associated ramdisk and
      kernel image according to its architecture and platform. When it does
      appear that the correct image is associated, we also need to check that
      there is only image in Glance with that name.
options:
    images:
        required: true
        description:
            - A list of images from Glance
        type: list
    nodes:
        required: true
        description:
            - A list of nodes from Ironic
        type: list
    deploy_kernel_name_base:
        required: true
        description:
            - Base name of kernel image
        type: string
    deploy_ramdisk_name_base:
        required: true
        description:
            - Base name of ramdisk image
        type: string

author: Jeremy Freudberg
'''

EXAMPLES = '''
- hosts: undercloud
  tasks:
    - name: Check Ironic boot config
      check_ironic_boot_config:
        images: "{{ lookup('glance_images', wantlist=True) }}"
        nodes: "{{ lookup('ironic_nodes', wantlist=True) }}"
        deploy_kernel_name_base: " {{ deploy_kernel_name_base }} "
        deploy_ramdisk_name_base: " {{ deploy_ramdisk_name_base }} "
'''


def _name_helper(basename, arch=None, platform=None):
    # TODO(jfreud): add support for non-Glance ironic-python-agent images
    # TODO(jfreud): delete in favor of (eventual) tripleo-common equivalent
    if arch and platform:
        basename = platform + '-' + arch + '-' + basename
    elif arch:
        basename = arch + '-' + basename
    return basename


def _all_possible_names(arch, platform, image_name_base):
    # TODO(jfreud): delete in favor of (eventual) tripleo-common equivalent
    if arch:
        if platform:
            yield _name_helper(image_name_base, arch=arch, platform=platform)
        yield _name_helper(image_name_base, arch=arch)
    yield _name_helper(image_name_base)


MISMATCH = (
    "\nNode {} has an incorrectly configured driver_info/deploy_{}. Expected "
    "{} but got {}."
)

NO_CANDIDATES = (
    "\nNode {} has an incorrectly configured driver_info/deploy_{}. Got {}, "
    "but cannot validate because could not find any suitable {} images in "
    "Glance."
)

DUPLICATE_NAME = (
    "\nNode {} appears to have a correctly configured driver_info/deploy_{} "
    "but the presence of more than one image in Glance with the name '{}' "
    "prevents the certainty of this."
)


def validate_boot_config(images,
                         nodes,
                         deploy_kernel_name_base,
                         deploy_ramdisk_name_base):
    errors = []

    image_map = {deploy_kernel_name_base: 'kernel',
                 deploy_ramdisk_name_base: 'ramdisk'}

    image_name_to_id = collections.defaultdict(list)
    for image in images:
        image_name_to_id[image["name"]].append(image["id"])

    for image_name_base, image_type in image_map.items():
        for node in nodes:
            actual_image_id = (
                node["driver_info"].get("deploy_%s" % image_type, None)
            )
            arch = node["properties"].get("cpu_arch", None)
            platform = node["extra"].get("tripleo_platform", None)

            candidates = [name for name in
                          _all_possible_names(arch, platform, image_name_base)
                          if name in image_name_to_id.keys()]
            if not candidates:
                errors.append(
                    NO_CANDIDATES.format(
                        node["uuid"],
                        image_type,
                        actual_image_id,
                        image_type
                    )
                )
                continue

            expected_image_name = candidates[0]
            expected_image_id = image_name_to_id[expected_image_name][0]

            if expected_image_id != actual_image_id:
                errors.append(
                    MISMATCH.format(
                        node["uuid"],
                        image_type,
                        expected_image_id,
                        actual_image_id or "None"
                    )
                )
            elif len(image_name_to_id[expected_image_name]) > 1:
                errors.append(
                    DUPLICATE_NAME.format(
                        node["uuid"],
                        image_type,
                        expected_image_name
                    )
                )

    return errors


def main():
    module = AnsibleModule(argument_spec=dict(
        images=dict(required=True, type='list'),
        nodes=dict(required=True, type='list'),
        deploy_kernel_name_base=dict(required=True, type='str'),
        deploy_ramdisk_name_base=dict(required=True, type='str')
    ))

    images = module.params.get('images')
    nodes = module.params.get('nodes')
    deploy_kernel_name_base = module.params.get('deploy_kernel_name_base')
    deploy_ramdisk_name_base = module.params.get('deploy_ramdisk_name_base')

    errors = validate_boot_config(
        images, nodes, deploy_kernel_name_base, deploy_ramdisk_name_base)

    if errors:
        module.fail_json(msg="".join(errors))
    else:
        module.exit_json()


if __name__ == '__main__':
    main()
