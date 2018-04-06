#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import itertools
import netaddr
import os.path
import yaml

import six

from ansible.module_utils.basic import AnsibleModule
from os_net_config import validator

from tripleo_validations.utils import get_nested


DOCUMENTATION = '''
---
module: network_environment
short_description: Validate networking templates
description:
    - Performs networking-related checks on a set of TripleO templates
options:
    netenv_path:
        required: true
        description:
            - The path of the base network environment file
        type: str
    plan_env_path:
        required: true
        description:
            - The path of the plan environment file
        type: str
    ip_pools_path:
        required: true
        description:
            - The path of the IP pools network environment file
        type: str
    template_files:
        required: true
        description:
            - A list of template files and contents
        type: list
author: "Tomas Sedovic, Martin André, Florian Fuchs"
'''

EXAMPLES = '''
- hosts: webservers
  tasks:
    - name: Check the Network environment
      network_environment:
        netenv_path: environments/network-environment.yaml
        template_files: "{{ lookup('tht') }}"
        plan_env_path: plan-environment.yaml
        ip_pools_path: environments/ips-from-pool-all.yaml
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


def validate(netenv_path, template_files):
    network_data, nic_configs, errors = open_network_environment_files(
        netenv_path, template_files)
    errors.extend(validate_network_environment(network_data, nic_configs))
    return errors


def validate_network_environment(network_data, nic_configs):
    errors = []

    cidrinfo = {}
    poolsinfo = {}
    vlaninfo = {}
    staticipinfo = {}

    for item, data in six.iteritems(network_data.get('parameter_defaults',
                                                     {})):
        if item.endswith('NetCidr'):
            cidrinfo[item] = data
        elif item.endswith('AllocationPools'):
            poolsinfo[item] = data
        elif item.endswith('NetworkVlanID'):
            vlaninfo[item] = data
        elif item.endswith('IPs'):
            staticipinfo[item] = data

    for nic_config_name, nic_config_path, nic_config in nic_configs:
        errors.extend(check_nic_configs(nic_config_path, nic_config))

    errors.extend(check_cidr_overlap(cidrinfo.values()))
    errors.extend(
        check_allocation_pools_pairing(
            network_data.get('parameter_defaults', {}), poolsinfo))
    errors.extend(check_static_ip_pool_collision(staticipinfo, poolsinfo))
    errors.extend(check_vlan_ids(vlaninfo))
    errors.extend(check_static_ip_in_cidr(cidrinfo, staticipinfo))
    errors.extend(duplicate_static_ips(staticipinfo))

    return errors


def check_nic_configs(path, nic_data):
    errors = []

    if not isinstance(nic_data, collections.Mapping):
        return ["The nic_data parameter must be a dictionary."]

    # Look though every resources bridges and make sure there is only a single
    # bond per bridge and only 1 interface per bridge if there are no bonds.
    resources = nic_data.get('resources')
    if not isinstance(resources, collections.Mapping):
        return ["The nic_data must contain the 'resources' key and it must be "
                "a dictionary."]
    for name, resource in six.iteritems(resources):
        try:
            nested_path = [
                ('properties', collections.Mapping, 'dictionary'),
                ('config', collections.Mapping, 'dictionary'),
                ('network_config', collections.Iterable, 'list'),
            ]
            bridges = get_nested(resource, name, nested_path)
        except ValueError as e:
            errors.append('{}'.format(e))
            continue
        # Not all resources contain a network config:
        if not bridges:
            continue

        # Validate the os_net_config object against the schema
        v_errors = validator.validate_config(bridges, path)
        errors.extend(v_errors)
        if len(v_errors) > 0:
            continue

        # If we get here, the nic config file conforms to the schema and
        # there is no more need to check for existence and type of
        # properties.
        for bridge in bridges:
            if bridge['type'] == 'ovs_bridge':
                bond_count = 0
                interface_count = 0
                for bridge_member in bridge['members']:
                    if bridge_member['type'] in ('ovs_bond', 'ovs_dpdk_bond'):
                        bond_count += 1
                    elif bridge_member['type'] == 'interface':
                        interface_count += 1
                    else:
                        pass

                if bond_count >= 2:
                    errors.append(
                        'Invalid bonding: There are >= 2 bonds for'
                        ' bridge {} of resource {} in {}'.format(
                            bridge['name'], name, path))
                if bond_count == 0 and interface_count > 1:
                    errors.append(
                        'Invalid interface: When not using a bond, '
                        'there can only be 1 interface for bridge {} '
                        'of resource {} in {}'.format(
                            bridge['name'], name, path))
                if bond_count == 0 and interface_count == 0:
                    errors.append(
                        'Invalid config: There must be at least '
                        '1 interface or 1 bond for bridge {}'
                        'of resource {} in {}'.format(
                            bridge['name'], name, path))
    return errors


def check_cidr_overlap(networks):
    errors = []
    objs = []
    if not isinstance(networks, collections.Iterable):
        return ["The argument must be iterable."]
    for x in networks:
        try:
            objs.append(netaddr.IPNetwork(x))
        except (ValueError, TypeError):
            errors.append('Invalid network: {}'.format(x))

    for net1, net2 in itertools.combinations(objs, 2):
        if (net1 in net2 or net2 in net1):
            errors.append(
                'Networks {} and {} overlap.'
                .format(net1, net2))
    return errors


def check_allocation_pools_pairing(filedata, pools):
    if not isinstance(filedata, collections.Mapping):
        return ["The `filedata` argument must be a dictionary."]
    if not isinstance(pools, collections.Mapping):
        return ["The `pools` argument must be a dictionary."]
    errors = []
    for poolitem, pooldata in six.iteritems(pools):
        pool_objs = []
        if not isinstance(pooldata, collections.Iterable):
            errors.append('The IP ranges in {} must form a list.'
                          .format(poolitem))
            continue

        # Check IP range format
        for dict_range in pooldata:
            try:
                pool_objs.append(netaddr.IPRange(
                    netaddr.IPAddress(dict_range['start']),
                    netaddr.IPAddress(dict_range['end'])))
            except Exception:
                errors.append("Invalid format of the IP range in {}: {}"
                              .format(poolitem, dict_range))
                continue

        # Check if CIDR is specified and IP network is valid
        subnet_item = poolitem.split('AllocationPools')[0] + 'NetCidr'
        try:
            network = filedata[subnet_item]
            subnet_obj = netaddr.IPNetwork(network)
        except KeyError:
            errors.append('The {} CIDR is not specified for {}.'
                          .format(subnet_item, poolitem))
            continue
        except Exception:
            errors.append('Invalid IP network: {}'.format(network))
            continue

        for range in pool_objs:
            # Check if pool is included in subnet
            if range not in subnet_obj:
                errors.append('Allocation pool {} {} outside of subnet'
                              ' {}: {}'.format(poolitem,
                                               pooldata,
                                               subnet_item,
                                               subnet_obj))
                break

            # Check for overlapping pools
            for other in [r for r in pool_objs if r != range]:
                if range.first in other or range.last in other:
                    errors.append('Some pools in {} are overlapping.'.format(
                                  poolitem))
                    break

    return errors


def check_static_ip_pool_collision(static_ips, pools):
    """Statically defined IP address must not conflict with allocation pools.

    The allocation pools come as a dict of items in the following format:

    InternalApiAllocationPools: [
        {'start': '10.35.191.150', 'end': '10.35.191.240'}
    ]

    The static IP addresses are dicts of:

    ComputeIPs: {
        'internal_api': ['10.35.191.100', etc.],
        'storage': ['192.168.100.45', etc.]
    }
    """
    if not isinstance(static_ips, collections.Mapping):
        return ["The static IPs input must be a dictionary."]
    if not isinstance(pools, collections.Mapping):
        return ["The Pools input must be a dictionary."]
    errors = []
    pool_ranges = []
    for pool_name, ranges in six.iteritems(pools):
        if not isinstance(ranges, collections.Iterable):
            errors.append("The IP ranges in {} must form a list."
                          .format(pool_name))
            continue
        for allocation_range in ranges:
            try:
                ip_range = netaddr.IPRange(allocation_range['start'],
                                           allocation_range['end'])
            except Exception:
                errors.append("Invalid format of the IP range in {}: {}"
                              .format(pool_name, allocation_range))
                continue
            pool_ranges.append((pool_name, ip_range))

    for role, services in six.iteritems(static_ips):
        if not isinstance(services, collections.Mapping):
            errors.append("The {} must be a dictionary.".format(role))
            continue
        for service, ips in six.iteritems(services):
            if not isinstance(ips, collections.Iterable):
                errors.append("The {}->{} must be an array."
                              .format(role, service))
                continue
            for ip in ips:
                try:
                    ip = netaddr.IPAddress(ip)
                except netaddr.AddrFormatError as e:
                    errors.append("{} is not a valid IP address: {}"
                                  .format(ip, e))
                    continue
                ranges_with_conflict = ranges_conflicting_with_ip(
                    ip, pool_ranges)
                if ranges_with_conflict:
                    for pool_name, ip_range in ranges_with_conflict:
                        msg = "IP address {} from {}[{}] is in the {} pool."
                        errors.append(msg.format(
                            ip, role, service, pool_name))
    return errors


def ranges_conflicting_with_ip(ip_address, ip_ranges):
    """Check for all conflicts of the IP address conflicts.

    This takes a single IP address and a list of `(pool_name,
    netenv.IPRange)`s.

    We return all ranges that the IP address conflicts with. This is to
    improve the final error messages.
    """
    return [(pool_name, ip_range) for (pool_name, ip_range) in ip_ranges
            if ip_address in ip_range]


def check_vlan_ids(vlans):
    if not isinstance(vlans, collections.Mapping):
        return ["The vlans parameter must be a dictionary."]
    errors = []
    invertdict = {}
    for k, v in six.iteritems(vlans):
        if v not in invertdict:
            invertdict[v] = k
        else:
            errors.append('Vlan ID {} ({}) already exists in {}'.format(
                v, k, invertdict[v]))
    return errors


def check_static_ip_in_cidr(networks, static_ips):
    """Check all static IP addresses are from the corresponding network range.

    """
    if not isinstance(networks, collections.Mapping):
        return ["The networks argument must be a dictionary."]
    if not isinstance(static_ips, collections.Mapping):
        return ["The static_ips argument must be a dictionary."]
    errors = []
    network_ranges = {}
    # TODO(shadower): Refactor this so networks are always valid and already
    # converted to `netaddr.IPNetwork` here. Will be useful in the other
    # checks.
    for name, cidr in six.iteritems(networks):
        try:
            network_ranges[name] = netaddr.IPNetwork(cidr)
        except Exception:
            errors.append("Network '{}' has an invalid CIDR: '{}'"
                          .format(name, cidr))
    for role, services in six.iteritems(static_ips):
        if not isinstance(services, collections.Mapping):
            errors.append("The {} must be a dictionary.".format(role))
            continue
        for service, ips in six.iteritems(services):
            range_name = service.title().replace('_', '') + 'NetCidr'
            if range_name in network_ranges:
                if not isinstance(ips, collections.Iterable):
                    errors.append("The {}->{} must be a list."
                                  .format(role, service))
                    continue
                for ip in ips:
                    if ip not in network_ranges[range_name]:
                        errors.append(
                            "The IP address {} is outside of the {} range: {}"
                            .format(ip, range_name, networks[range_name]))
            else:
                errors.append(
                    "Service '{}' does not have a "
                    "corresponding range: '{}'.".format(service, range_name))
    return errors


def duplicate_static_ips(static_ips):
    errors = []
    if not isinstance(static_ips, collections.Mapping):
        return ["The static_ips argument must be a dictionary."]
    ipset = collections.defaultdict(list)
    # TODO(shadower): we're doing this netsted loop multiple times. Turn it
    # into a generator or something.
    for role, services in six.iteritems(static_ips):
        if not isinstance(services, collections.Mapping):
            errors.append("The {} must be a dictionary.".format(role))
            continue
        for service, ips in six.iteritems(services):
            if not isinstance(ips, collections.Iterable):
                errors.append("The {}->{} must be a list."
                              .format(role, service))
                continue
            for ip in ips:
                ipset[ip].append((role, service))
    for ip, sources in six.iteritems(ipset):
        if len(sources) > 1:
            msg = "The {} IP address was entered multiple times: {}."
            formatted_sources = ("{}[{}]"
                                 .format(*source) for source in sources)
            errors.append(msg.format(ip, ", ".join(formatted_sources)))
    return errors


def validate_node_pool_size(plan_env_path, ip_pools_path, template_files):
    warnings = []
    plan_env = yaml.safe_load(template_files[plan_env_path])
    ip_pools = yaml.safe_load(template_files[ip_pools_path])

    param_defaults = plan_env.get('parameter_defaults')
    node_counts = {
        param.replace('Count', ''): count
        for param, count in six.iteritems(param_defaults)
        if param.endswith('Count') and count > 0
    }

    # TODO(akrivoka): There are a lot of inconsistency issues with parameter
    # naming in THT :( Once those issues are fixed, this block should be
    # removed.
    if 'ObjectStorage' in node_counts:
        node_counts['SwiftStorage'] = node_counts['ObjectStorage']
        del node_counts['ObjectStorage']

    param_defaults = ip_pools.get('parameter_defaults')
    role_pools = {
        param.replace('IPs', ''): pool
        for param, pool in six.iteritems(param_defaults)
        if param.endswith('IPs') and param.replace('IPs', '') in node_counts
    }

    for role, node_count in six.iteritems(node_counts):
        try:
            pools = role_pools[role]
        except KeyError:
            warnings.append(
                "Found {} node(s) assigned to '{}' role, but no static IP "
                "pools defined.".format(node_count, role)
            )
            continue
        for pool_name, pool_ips in six.iteritems(pools):
            if len(pool_ips) < node_count:
                warnings.append(
                    "Insufficient number of IPs in '{}' pool for '{}' role: "
                    "{} IP(s) found in pool, but {} nodes assigned to role."
                        .format(pool_name, role, len(pool_ips), node_count)
                )

    return warnings


def main():
    module = AnsibleModule(argument_spec=dict(
        netenv_path=dict(required=True, type='str'),
        plan_env_path=dict(required=True, type='str'),
        ip_pools_path=dict(required=True, type='str'),
        template_files=dict(required=True, type='list')
    ))

    netenv_path = module.params.get('netenv_path')
    plan_env_path = module.params.get('plan_env_path')
    ip_pools_path = module.params.get('ip_pools_path')
    template_files = {name: content[1] for (name, content) in
                      module.params.get('template_files')}

    errors = validate(netenv_path, template_files)
    warnings = []

    try:
        warnings = validate_node_pool_size(plan_env_path, ip_pools_path,
                                           template_files)
    except Exception as e:
        errors.append("{}".format(e))

    if errors:
        module.fail_json(msg="\n".join(errors))
    else:
        module.exit_json(
            msg="No errors found for the '{}' file.".format(netenv_path),
            warnings=warnings,
        )


if __name__ == '__main__':
    main()
