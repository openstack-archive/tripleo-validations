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

from ansible.module_utils.basic import AnsibleModule  # noqa

DOCUMENTATION = '''
---
module: check_flavors
short_description: Check that assigned flavors exist and are configured
description:
    - Validate that the flavors assigned to roles exist and have the correct
    settings. Right now, that means that boot_option is set to 'local', or
    if set to 'netboot', issue a warning.
options:
    roles_info:
        required: true
        description:
            - A list of role info
        type: list
    flavors:
        required: true
        description:
            - A dictionary of flavors from Nova
        type: dict

author: "Brad P. Crochet"
'''

EXAMPLES = '''
- hosts: undercloud
  tasks:
    - name: Check the flavors
      check_flavors:
        roles_info: "{{ lookup('roles_info', wantlist=True) }}"
        flavors: "{{ lookup('nova_flavors', wantlist=True) }}"
'''


def validate_roles_and_flavors(roles_info, flavors):
    """Check if roles info is correct

      :param roles_info: list of role data
      :param flavors: dictionary of flavors
      :returns result: Flavors and scale
               warnings: List of warning messages
               errors: List of error messages
    """

    result = {}
    errors = []
    warnings = []

    message = "Flavor '{1}' provided for the role '{0}', does not exist"
    missing_message = "Role '{0}' is in use, but has no flavor assigned"
    warning_message = (
        'Flavor {0} "capabilities:boot_option" is set to '
        '"netboot". Nodes will PXE boot from the ironic '
        'conductor instead of using a local bootloader. '
        'Make sure that enough nodes are marked with the '
        '"boot_option" capability set to "netboot".')

    for role in roles_info:
        target = role.get('name')
        flavor_name = role.get('flavor')
        scale = role.get('count', 0)

        if flavor_name is None or not scale:
            if scale:
                errors.append(missing_message.format(target))
            continue

        old_flavor_name, old_scale = result.get(flavor_name, (None, None))

        if old_flavor_name:
            result[flavor_name] = (old_flavor_name, scale)
        else:
            flavor = flavors.get(flavor_name)

            if flavor:
                keys = flavor.get('keys', None)
                if keys:
                    if keys.get('capabilities:boot_option', '') \
                            == 'netboot':
                        warnings.append(
                            warning_message.format(flavor_name))

                result[flavor_name] = (flavor, scale)
            else:
                errors.append(message.format(target, flavor_name))

    return result, warnings, errors


def main():
    module = AnsibleModule(argument_spec=dict(
        roles_info=dict(required=True, type='list'),
        flavors=dict(required=True, type='dict')
    ))

    roles_info = module.params.get('roles_info')
    flavors = module.params.get('flavors')

    flavor_result, warnings, errors = validate_roles_and_flavors(roles_info,
                                                                 flavors)

    if errors:
        module.fail_json(msg="\n".join(errors))
    elif warnings:
        module.exit_json(warnings="\n".join(warnings))
    else:
        module.exit_json(
            msg="All flavors configured on roles",
            flavors=flavor_result)


if __name__ == '__main__':
    main()
