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

import collections
import os.path
import yaml

import six

from ansible.module_utils.basic import AnsibleModule  # noqa
from tripleo_validations import utils

DOCUMENTATION = '''
---
module: switch_vlans
short_description: Check configured VLANs against Ironic introspection data
description:
    - Validate that the VLANs defined in TripleO nic config files are in the
    LLDP info received from network switches.  The LLDP data is stored in
    Ironic introspection data per interface.
options:
    path:
        required: true
        description:
            - The path of the base network environment file
        type: str
    template_files:
        required: true
        description:
            - A list of template files and contents
        type: list
    introspection_data:
        required: true
        description:
            - Introspection data for all nodes
        type: list

author: "Bob Fournier"
'''

EXAMPLES = '''
- hosts: undercloud
  tasks:
    - name: Check that switch vlans are present if used in nic-config files
      network_environment:
        path: environments/network-environment.yaml
        template_files: "{{ lookup('tht') }}"
        introspection_data: "{{ lookup('introspection_data',
            auth_url=auth_url.value, password=password.value) }}"
'''


def open_network_environment_files(netenv_path, template_files):
    errors = []

    try:
        network_data = yaml.safe_load(template_files[netenv_path])
    except Exception as e:
        return ({}, {}, ["Can't open network environment file '{}': {}"
                         .format(netenv_path, e)])
    nic_configs = []
    resource_registry = network_data.get('resource_registry', {})
    for nic_name, relative_path in six.iteritems(resource_registry):
        if nic_name.endswith("Net::SoftwareConfig"):
            nic_config_path = os.path.normpath(
                os.path.join(os.path.dirname(netenv_path), relative_path))
            try:
                nic_configs.append((
                    nic_name, nic_config_path,
                    yaml.safe_load(template_files[nic_config_path])))
            except Exception as e:
                errors.append(
                    "Can't open the resource '{}' reference file '{}': {}"
                    .format(nic_name, nic_config_path, e))

    return (network_data, nic_configs, errors)


def validate_switch_vlans(netenv_path, template_files, introspection_data):
    """Check if VLAN exists in introspection data for node

      :param netenv_path: path to network_environment file
      :param template_files: template files being checked
      :param introspection_data: introspection data for all node
      :returns warnings: List of warning messages
               errors: List of error messages
    """

    network_data, nic_configs, errors =\
        open_network_environment_files(netenv_path, template_files)
    warnings = []
    vlans_in_templates = False

    # Store VLAN IDs from network-environment.yaml.
    vlaninfo = {}
    for item, data in six.iteritems(network_data.get('parameter_defaults',
                                                     {})):
        if item.endswith('NetworkVlanID'):
            vlaninfo[item] = data

    # Get the VLANs which are actually used in nic configs
    for nic_config_name, nic_config_path, nic_config in nic_configs:
        resources = nic_config.get('resources')
        if not isinstance(nic_config, collections.Mapping):
            return [], ["nic_config parameter must be a dictionary."]

        if not isinstance(resources, collections.Mapping):
            return [], ["The nic_data must contain the 'resources' key "
                        "and it must be a dictionary."]
        for name, resource in six.iteritems(resources):
            try:
                nested_path = [
                    ('properties', collections.Mapping, 'dictionary'),
                    ('config', collections.Mapping, 'dictionary'),
                    ('network_config', collections.Iterable, 'list'),
                ]
                nw_config = utils.get_nested(resource, name, nested_path)
            except ValueError as e:
                errors.append('{}'.format(e))
                continue
            # Not all resources contain a network config:
            if not nw_config:
                continue

            for elem in nw_config:
                # VLANs will be in bridge
                if elem['type'] == 'ovs_bridge' \
                        or elem['type'] == 'linux_bridge':
                    for member in elem['members']:
                        if member['type'] != 'vlan':
                            continue

                        vlans_in_templates = True
                        vlan_id_str = member['vlan_id']
                        vlan_id = vlaninfo[vlan_id_str['get_param']]

                        msg, result = vlan_exists_on_switch(
                            vlan_id, introspection_data)
                        warnings.extend(msg)

                        if not msg and result is False:
                            errors.append(
                                "VLAN ID {} not on attached switch".format(
                                    vlan_id))

    if not vlans_in_templates:
        warnings.append("No VLANs are used on templates files")

    return warnings, errors


def vlan_exists_on_switch(vlan_id, introspection_data):
    """Check if VLAN exists in introspection data

     :param vlan_id: VLAN id
     :param introspection_data: introspection data for all nodes
     :returns msg: Error or warning message
              result: boolean indicating if VLAN was found
     """

    for node, content in introspection_data.items():
        node_valid_lldp = False
        try:
            data = yaml.safe_load(content)
        except Exception as e:
            return ["Can't open introspection data : {}" .format(e)], False

        all_interfaces = data.get('all_interfaces', [])

        # Check lldp data on all interfaces for this vlan ID
        for interface in all_interfaces:
            lldp_proc = all_interfaces[interface].get('lldp_processed', {})

            if lldp_proc:
                node_valid_lldp = True

                switch_vlans = lldp_proc.get('switch_port_vlans', [])
                if switch_vlans:
                    if any(vlan['id'] == vlan_id for vlan in switch_vlans):
                        return [], True

        # If no lldp data for node return warning, not possible to locate vlan
        if not node_valid_lldp:
            node_uuid = node.split("-", 1)[1]
            return ["LLDP data not available for node {}".format(node_uuid)],\
                False

    return [], False  # could not find VLAN ID


def main():
    module = AnsibleModule(argument_spec=dict(
        path=dict(required=True, type='str'),
        template_files=dict(required=True, type='list'),
        introspection_data=dict(required=True, type='list')
    ))

    netenv_path = module.params.get('path')
    template_files = {name: content[1] for (name, content) in
                      module.params.get('template_files')}
    introspection_data = {name: content[1] for (name, content) in
                          module.params.get('introspection_data')}

    warnings, errors = validate_switch_vlans(netenv_path, template_files,
                                             introspection_data)

    if errors:
        module.fail_json(msg="\n".join(errors))
    elif warnings:
        module.exit_json(warnings="\n".join(warnings))
    else:
        module.exit_json(msg="All VLANs configured on attached switches")


if __name__ == '__main__':
    main()
