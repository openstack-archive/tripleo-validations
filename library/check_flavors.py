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
from yaml import safe_load as yaml_safe_load

import re

DOCUMENTATION = '''
---
module: check_flavors
short_description: Check that assigned flavors exist and are configured
description:
    - Validate that the flavors assigned to roles exist and have the correct
      settings. Right now, that means that boot_option is unset or set to
     'local', or if set to 'netboot', issue a warning.
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
    custom_resource_class = None
    custom_resource_class_val = None

    message = "Flavor '{1}' provided for the role '{0}', does not exist"
    missing_message = "Role '{0}' is in use, but has no flavor assigned"
    warning_message = (
        'Flavor {0} "capabilities:boot_option" is set to '
        '"netboot". Nodes will PXE boot from the ironic '
        'conductor instead of using a local bootloader. '
        'Make sure that enough nodes are marked with the '
        '"boot_option" capability set to "netboot".')
    resource_class_missing = (
        'Flavor {0} does not have a custom resource class '
        'associated with it')
    resource_class_name_incorrect = (
        'Flavor {0} has an incorrectly named custom '
        'resource class associated with it')
    resource_class_value_incorrect = (
        'Flavor {0} has a resource class that is not '
        'offering exactly 1 resource')
    disable_standard_scheduling = (
        'Flavor {0} has to have scheduling based on '
        'standard properties disabled by setting '
        'resources:VCPU=0 resources:MEMORY_MB=0 '
        'resources:DISK_GB=0 in the flavor property')

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
                    # check if the baremetal flavor has custom resource class
                    # required for scheduling since queens
                    resource_specs = {key.split(
                        "resources:", 1)[-1]: val
                        for key, val in keys.items()
                        if key.startswith("resources:")}
                    if not resource_specs:
                        errors.append(resource_class_missing.format(
                            flavor_name))
                    else:
                        for key, val in resource_specs.items():
                            if key.startswith("CUSTOM_"):
                                custom_resource_class = True
                                match = re.match('CUSTOM_[A-Z_]+', key)
                                if match is None:
                                    errors.append(
                                        resource_class_name_incorrect,
                                        flavor_name)
                                else:
                                    if int(val) == 1:
                                        custom_resource_class_val = True
                        if not custom_resource_class:
                            errors.append(resource_class_missing.format(
                                flavor_name))
                        if key not in ["DISK_GB", "MEMORY_MB", "VCPU"] and \
                                not custom_resource_class_val:
                            errors.append(resource_class_value_incorrect.
                                          format(flavor_name))
                        disk = resource_specs.get("DISK_GB", None)
                        memory = resource_specs.get("MEMORY_MB", None)
                        vcpu = resource_specs.get("VCPU", None)
                        if any(int(resource) != 0 for resource in [disk,
                               memory, vcpu]):
                            errors.append(disable_standard_scheduling.
                                          format(flavor_name))

                result[flavor_name] = (flavor, scale)
            else:
                errors.append(message.format(target, flavor_name))

    return result, warnings, errors


def main():
    module = AnsibleModule(
        argument_spec=yaml_safe_load(DOCUMENTATION)['options']
    )

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
