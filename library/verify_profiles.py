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
module: verify_profiles
short_description: Check that profiles have enough nodes
description:
    - Validate that the profiles assigned have enough nodes available.
options:
    nodes:
        required: true
        description:
            - A list of nodes
        type: list
    flavors:
        required: true
        description:
            - A dictionary of flavors
        type: dict

author: "Brad P. Crochet"
'''

EXAMPLES = '''
- hosts: undercloud
  tasks:
    - name: Collect the flavors
      check_flavors:
        roles_info: "{{ lookup('roles_info', wantlist=True) }}"
        flavors: "{{ lookup('nova_flavors', wantlist=True) }}"
      register: flavor_result
    - name: Check the profiles
      verify_profiles:
        nodes: "{{ lookup('ironic_nodes', wantlist=True) }}"
        flavors: flavor_result.flavors
'''


def _capabilities_to_dict(caps):
    """Convert the Node's capabilities into a dictionary."""
    if not caps:
        return {}
    if isinstance(caps, dict):
        return caps
    return dict([key.split(':', 1) for key in caps.split(',')])


def _node_get_capabilities(node):
    """Get node capabilities."""
    return _capabilities_to_dict(
        node['properties'].get('capabilities'))


def verify_profiles(nodes, flavors):
    """Check if roles info is correct

      :param nodes: list of nodes
      :param flavors: dictionary of flavors
      :returns warnings: List of warning messages
               errors: List of error messages
    """
    errors = []
    warnings = []

    bm_nodes = {node['uuid']: node for node in nodes
                if node['provision_state'] in ('available', 'active')}

    free_node_caps = {uu: _node_get_capabilities(node)
                      for uu, node in bm_nodes.items()}

    profile_flavor_used = False
    for flavor_name, (flavor, scale) in flavors.items():
        if not scale:
            continue

        profile = None
        keys = flavor.get('keys')
        if keys:
            profile = keys.get('capabilities:profile')

        if not profile and len(flavors) > 1:
            message = ('Error: The {flavor} flavor has no profile '
                       'associated.\n'
                       'Recommendation: assign a profile with openstack '
                       'flavor set --property '
                       '"capabilities:profile"="PROFILE_NAME" {flavor}')

            errors.append(message.format(flavor=flavor_name))
            continue

        profile_flavor_used = True

        assigned_nodes = [uu for uu, caps in free_node_caps.items()
                          if caps.get('profile') == profile]
        required_count = scale - len(assigned_nodes)

        if required_count < 0:
            warnings.append('%d nodes with profile %s won\'t be used '
                            'for deployment now' % (-required_count,
                                                    profile))
            required_count = 0

        for uu in assigned_nodes:
            free_node_caps.pop(uu)

        if required_count > 0:
            message = ('Error: only {total} of {scale} requested ironic '
                       'nodes are tagged to profile {profile} (for flavor '
                       '{flavor}).\n'
                       'Recommendation: tag more nodes using openstack '
                       'baremetal node set --property "capabilities='
                       'profile:{profile}" <NODE ID>')
            errors.append(message.format(total=scale - required_count,
                                         scale=scale,
                                         profile=profile,
                                         flavor=flavor_name))

    nodes_without_profile = [uu for uu, caps in free_node_caps.items()
                             if not caps.get('profile')]
    if nodes_without_profile and profile_flavor_used:
        warnings.append("There are %d ironic nodes with no profile that "
                        "will not be used: %s" % (
                            len(nodes_without_profile),
                            ', '.join(nodes_without_profile)))

    return warnings, errors


def main():
    module = AnsibleModule(argument_spec=dict(
        nodes=dict(required=True, type='list'),
        flavors=dict(required=True, type='dict')
    ))

    nodes = module.params.get('nodes')
    flavors = module.params.get('flavors')

    warnings, errors = verify_profiles(nodes,
                                       flavors)

    if errors:
        module.fail_json(msg="\n".join(errors))
    elif warnings:
        module.exit_json(warnings="\n".join(warnings))
    else:
        module.exit_json(
            msg="No profile errors detected.")


if __name__ == '__main__':
    main()
