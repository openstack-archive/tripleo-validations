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


import library.network_environment as validation
from tripleo_validations.tests import base


class TestNicConfigs(base.TestCase):

    def test_non_dict(self):
        errors = validation.check_nic_configs("controller.yaml", None)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The nic_data parameter must be a dictionary.',
                         errors[0])

    def _test_resources_invalid(self, nic_data):
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertEqual("The nic_data must contain the 'resources' key and it"
                         " must be a dictionary.", errors[0])

    def test_resources_dict(self):
        self._test_resources_invalid({})
        self._test_resources_invalid({'resources': None})

    def test_resource_not_dict(self):
        nic_data = {'resources': {'foo': None}}
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertEqual("'foo' is not a valid resource.", errors[0])

    def test_resource_config_not_dict(self):
        nic_data = {'resources': {'foo': {'properties': {'config': None}}}}
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertEqual("The 'config' property of 'foo' must be"
                         " a dictionary.", errors[0])

    def nic_data(self, bridges):
        return {
            'resources': {
                'foo': {
                    'properties': {
                        'config': {
                            'str_replace': {
                                'params': {
                                    '$network_config': {
                                        'network_config': bridges
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

    def test_network_config_not_list(self):
        nic_data = self.nic_data(None)
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("'foo' must be a list", errors[0])

    # See comment from 2018-11-22 in library/network_environment.py
    """
    def test_bridge_has_type(self):
        nic_data = self.nic_data([{
            'name': 'storage',
            'members': [],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("'type' is a required property", errors[0])

    def test_bridge_is_of_known_type(self):
        nic_data = self.nic_data([{
            'type': 'interface'
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("{'type': 'intreface'} is not valid", errors[0])

    def test_bridge_has_name(self):
        nic_data = self.nic_data([{
            'type': 'ovs_bridge',
            'members': [],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("'name' is a required property", errors[0])

    def test_bridge_has_only_known_properties(self):
        nic_data = self.nic_data([{
            'type': 'ovs_bridge',
            'name': 'storage',
            'member': [],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("Additional properties are not allowed"
                      " ('member' was unexpected)", errors[0])

    def test_ovs_bridge_has_members(self):
        nic_data = self.nic_data([{
            'name': 'storage',
            'type': 'ovs_bridge',
            'members': None,
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("members/type: 'None' is not of type 'array'",
                      errors[0])

    def test_ovs_bridge_members_dict(self):
        nic_data = self.nic_data([{
            'name': 'storage',
            'type': 'ovs_bridge',
            'members': [None],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("members/items/oneOf: None is not valid under any"
                      " of the given schemas", errors[0])

    def test_bonds_have_known_type(self):
        nic_data = self.nic_data([{
            'type': 'magic_bridge',
            'name': 'storage',
            'members': [{}],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("members/items/oneOf: {} is not valid under any"
                      " of the given schemas", errors[0])
    """

    def test_more_than_one_bond(self):
        nic_data = self.nic_data([{
            'type': 'ovs_bridge',
            'name': 'storage',
            'members': [
                {
                    'type': 'ovs_bond',
                    'name': 'bond0',
                    'members': [
                        {'type': 'interface', 'name': 'eth0'},
                        {'type': 'interface', 'name': 'eth1'},
                    ]
                }, {
                    'type': 'ovs_bond',
                    'name': 'bond1',
                    'members': [
                        {'type': 'interface', 'name': 'eth2'},
                        {'type': 'interface', 'name': 'eth3'},
                    ]
                },
            ],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('Invalid bonding: There are >= 2 bonds for bridge '
                      'storage', errors[0])

    def test_multiple_interfaces_without_bond(self):
        nic_data = self.nic_data([{
            'type': 'ovs_bridge',
            'name': 'storage',
            'members': [
                {'type': 'interface', 'name': 'eth0'},
                {'type': 'interface', 'name': 'eth1'},
            ],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('Invalid interface: When not using a bond, there can'
                      ' only be 1 interface for bridge storage', errors[0])

    def test_one_interface_without_bond(self):
        nic_data = self.nic_data([{
            'type': 'ovs_bridge',
            'name': 'storage',
            'members': [
                {'type': 'interface', 'name': 'eth0'},
            ],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual([], errors)

    # See comment from 2018-11-22 in library/network_environment.py
    """
    def test_one_bond_no_interfaces(self):
        nic_data = self.nic_data([{
            'type': 'ovs_bridge',
            'name': 'storage',
            'members': [
                {'type': 'ovs_bond', 'name': 'bond0', 'members': []},
            ],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual(len(errors), 1)
        self.assertIn('members/minItems: [] is too short', errors[0])
    """

    def test_one_bond_multiple_interfaces(self):
        nic_data = self.nic_data([{
            'type': 'ovs_bridge',
            'name': 'storage',
            'members': [
                {
                    'type': 'ovs_bond',
                    'name': 'bond0',
                    'members': [
                        {'type': 'interface', 'name': 'eth2'},
                        {'type': 'interface', 'name': 'eth3'},
                    ]
                },
                {'type': 'interface', 'name': 'eth0'},
                {'type': 'interface', 'name': 'eth1'},
            ],
        }])
        errors = validation.check_nic_configs("controller.yaml", nic_data)
        self.assertEqual([], errors)


class TestCheckCidrOverlap(base.TestCase):

    def test_empty(self):
        errors = validation.check_cidr_overlap([])
        self.assertEqual([], errors)

    def test_none(self):
        errors = validation.check_cidr_overlap(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual("The argument must be iterable.", errors[0])

    def test_network_none(self):
        errors = validation.check_cidr_overlap([None])
        self.assertEqual(len(errors), 1)
        self.assertEqual("Invalid network: None", errors[0])

    def test_single_network(self):
        errors = validation.check_cidr_overlap(['172.16.0.0/24'])
        self.assertEqual([], errors)

    def test_single_network_ipv6(self):
        errors = validation.check_cidr_overlap(['fd00:fd00:fd00:2000::/64'])
        self.assertEqual([], errors)

    def test_non_overlapping_networks(self):
        networks = ['172.16.0.0/24', '172.17.0.0/24']
        errors = validation.check_cidr_overlap(networks)
        self.assertEqual([], errors)

    def test_identical_networks(self):
        networks = ['172.16.0.0/24', '172.16.0.0/24']
        errors = validation.check_cidr_overlap(networks)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Networks 172.16.0.0/24 and 172.16.0.0/24 overlap.',
                         errors[0])

    def test_identical_networks_ipv6(self):
        networks = ['fd00:fd00:fd00:2000::/64', 'fd00:fd00:fd00:2000::/64']
        errors = validation.check_cidr_overlap(networks)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Networks fd00:fd00:fd00:2000::/64 and '
                         'fd00:fd00:fd00:2000::/64 overlap.',
                         errors[0])

    def test_first_cidr_is_subset_of_second_ipv6(self):
        networks = ['fd00:fd00:fd00:2000::/126', 'fd00:fd00:fd00:2000::/124']
        errors = validation.check_cidr_overlap(networks)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Networks fd00:fd00:fd00:2000::/126 and '
                         'fd00:fd00:fd00:2000::/124 overlap.',
                         errors[0])

    def test_first_cidr_is_subset_of_second(self):
        networks = ['172.16.10.0/24', '172.16.0.0/16']
        errors = validation.check_cidr_overlap(networks)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Networks 172.16.10.0/24 and 172.16.0.0/16 overlap.',
                         errors[0])

    def test_second_cidr_is_subset_of_first(self):
        networks = ['172.16.0.0/16', '172.16.10.0/24']
        errors = validation.check_cidr_overlap(networks)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Networks 172.16.0.0/16 and 172.16.10.0/24 overlap.',
                         errors[0])

    def test_second_cidr_is_subset_of_first_ipv6(self):
        networks = ['fd00:fd00:fd00:2000::/124', 'fd00:fd00:fd00:2000::/126']
        errors = validation.check_cidr_overlap(networks)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Networks fd00:fd00:fd00:2000::/124 and '
                         'fd00:fd00:fd00:2000::/126 overlap.',
                         errors[0])

    def test_multiple_overlapping_networks(self):
        networks = ['172.16.0.0/16', '172.16.10.0/24',
                    '172.16.11.0/23', '172.17.0.0/24']
        errors = validation.check_cidr_overlap(networks)
        self.assertEqual(len(errors), 3)
        self.assertEqual('Networks 172.16.0.0/16 and 172.16.10.0/24 overlap.',
                         errors[0])
        self.assertEqual('Networks 172.16.0.0/16 and 172.16.11.0/23 overlap.',
                         errors[1])
        self.assertEqual('Networks 172.16.10.0/24 and 172.16.11.0/23 overlap.',
                         errors[2])


class TestCheckAllocationPoolsPairing(base.TestCase):

    def test_empty(self):
        errors = validation.check_allocation_pools_pairing({}, {})
        self.assertEqual([], errors)

    def test_non_dict(self):
        errors = validation.check_allocation_pools_pairing(None, {})
        self.assertEqual(len(errors), 1)
        self.assertEqual('The `filedata` argument must be a dictionary.',
                         errors[0])
        errors = validation.check_allocation_pools_pairing({}, None)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The `pools` argument must be a dictionary.',
                         errors[0])

    def test_pool_range_not_list(self):
        pools = {'TestPools': None}
        errors = validation.check_allocation_pools_pairing({}, pools)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The IP ranges in TestPools must form a list.',
                         errors[0])

    def _test_pool_invalid_range(self, addr_range):
        filedata = {'TestNetCidr': '172.18.0.0/24'}
        pools = {'TestAllocationPools': [addr_range]}
        errors = validation.check_allocation_pools_pairing(filedata, pools)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Invalid format of the IP range in'
                         ' TestAllocationPools: {}'.format(addr_range),
                         errors[0])

    def test_pool_invalid_range(self):
        broken_ranges = [None,
                         {},
                         {'start': 'foo', 'end': 'bar'},
                         {'start': '10.0.0.1', 'end': '10.0.0.0'},
                         ]
        for addr_range in broken_ranges:
            self._test_pool_invalid_range(addr_range)

    def test_pool_with_correct_range(self):
        filedata = {
            'StorageNetCidr': '172.18.0.0/24',
        }
        pools = {
            'StorageAllocationPools': [
                {'start': '172.18.0.10', 'end': '172.18.0.200'}
            ]
        }
        errors = validation.check_allocation_pools_pairing(filedata, pools)
        self.assertEqual([], errors)

    def test_pool_without_cidr(self):
        filedata = {}
        pools = {
            'StorageAllocationPools': [
                {'start': '172.18.0.10', 'end': '172.18.0.200'}
            ]
        }
        errors = validation.check_allocation_pools_pairing(filedata, pools)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The StorageNetCidr CIDR is not specified for'
                         ' StorageAllocationPools.', errors[0])

    def test_pool_with_invalid_cidr(self):
        filedata = {
            'StorageNetCidr': 'breakit',
        }
        pools = {
            'StorageAllocationPools': [
                {'start': '172.18.0.10', 'end': '172.18.0.200'}
            ]
        }
        errors = validation.check_allocation_pools_pairing(filedata, pools)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Invalid IP network: breakit', errors[0])

    def test_pool_outside_cidr(self):
        filedata = {
            'StorageNetCidr': '172.18.0.0/25',
        }
        pools = {
            'StorageAllocationPools': [
                {'start': '172.18.0.10', 'end': '172.18.0.200'}
            ]
        }
        errors = validation.check_allocation_pools_pairing(filedata, pools)
        self.assertEqual(len(errors), 1)
        self.assertIn('outside of subnet StorageNetCidr', errors[0])

    def test_pool_outside_cidr_ipv6(self):
        filedata = {
            'StorageNetCidr': 'fd00:fd00:fd00:3000::10/125',
        }
        pools = {
            'StorageAllocationPools': [
                {'start': 'fd00:fd00:fd00:3000::10',
                 'end': 'fd00:fd00:fd00:3000::18'}
            ]
        }
        errors = validation.check_allocation_pools_pairing(filedata, pools)
        self.assertEqual(len(errors), 1)
        self.assertIn('outside of subnet StorageNetCidr', errors[0])

    def test_multiple_ranges_and_pools(self):
        filedata = {
            'StorageNetCidr': '172.18.0.0/24',
            'TenantNetCidr': '172.16.0.0/24',
        }
        pools = {
            'StorageAllocationPools': [
                {'start': '172.18.0.10', 'end': '172.18.0.20'},
                {'start': '172.18.0.100', 'end': '172.18.0.200'},
            ],
            'TenantAllocationPools': [
                {'start': '172.16.0.20', 'end': '172.16.0.30'},
                {'start': '172.16.0.70', 'end': '172.16.0.80'},
            ],
        }
        errors = validation.check_allocation_pools_pairing(filedata, pools)
        self.assertEqual([], errors)

    def test_pool_very_large_range_ipv6(self):
        filedata = {
            'StorageNetCidr': 'fd00:fd00:fd00:3000::/64',
        }
        pools = {
            'StorageAllocationPools': [
                {'start': 'fd00:fd00:fd00:3000::10',
                 'end': 'fd00:fd00:fd00:3000:ffff:ffff:ffff:fffe'}
            ]
        }
        errors = validation.check_allocation_pools_pairing(filedata, pools)
        self.assertEqual([], errors)

    def test_overlapping_pools(self):
        filedata = {
            'StorageNetCidr': '172.18.0.0/24',
        }
        pools = {
            'StorageAllocationPools': [
                {'start': '172.18.0.10', 'end': '172.18.0.30'},
                {'start': '172.18.0.20', 'end': '172.18.0.200'},
            ],
        }
        errors = validation.check_allocation_pools_pairing(filedata, pools)
        self.assertIn('Some pools in StorageAllocationPools are overlapping.',
                      errors[0])


class TestStaticIpPoolCollision(base.TestCase):

    def test_empty(self):
        errors = validation.check_static_ip_pool_collision({}, {})
        self.assertEqual([], errors)

    def test_non_dict(self):
        errors = validation.check_static_ip_pool_collision(None, {})
        self.assertEqual(len(errors), 1)
        self.assertEqual('The static IPs input must be a dictionary.',
                         errors[0])
        errors = validation.check_static_ip_pool_collision({}, None)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The Pools input must be a dictionary.',
                         errors[0])

    def test_pool_range_not_list(self):
        pools = {'TestPools': None}
        errors = validation.check_static_ip_pool_collision({}, pools)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The IP ranges in TestPools must form a list.',
                         errors[0])

    def _test_pool_invalid_range(self, addr_range):
        static_ips = {}
        pools = {'TestAllocationPools': [addr_range]}
        errors = validation.check_static_ip_pool_collision(static_ips, pools)
        self.assertEqual(len(errors), 1)
        self.assertEqual('Invalid format of the IP range in'
                         ' TestAllocationPools: {}'.format(addr_range),
                         errors[0])

    def test_pool_invalid_range(self):
        broken_ranges = [None,
                         {},
                         {'start': 'foo', 'end': 'bar'},
                         {'start': '10.0.0.1', 'end': '10.0.0.0'},
                         ]
        for addr_range in broken_ranges:
            self._test_pool_invalid_range(addr_range)

    def test_pool_with_correct_range(self):
        static_ips = {}
        pools = {
            'StorageAllocationPools': [
                {'start': '172.18.0.10', 'end': '172.18.0.200'}
            ]
        }
        errors = validation.check_static_ip_pool_collision(static_ips, pools)
        self.assertEqual([], errors)

    def test_static_ip_service_not_dict(self):
        static_ips = {'ComputeIPs': None}
        errors = validation.check_static_ip_pool_collision(static_ips, {})
        self.assertEqual(len(errors), 1)
        self.assertEqual('The ComputeIPs must be a dictionary.', errors[0])

    def test_static_ips_not_lists(self):
        static_ips = {
            'ComputeIPs': {
                'internal_api': None
            }
        }
        errors = validation.check_static_ip_pool_collision(static_ips, {})
        self.assertEqual(len(errors), 1)
        self.assertEqual('The ComputeIPs->internal_api must be an array.',
                         errors[0])

    def test_static_ips_not_parseable(self):
        static_ips = {
            'ComputeIPs': {
                'internal_api': ['nonsense', None, '270.0.0.1'],
            }
        }
        pools = {}
        errors = validation.check_static_ip_pool_collision(static_ips, pools)
        self.assertEqual(len(errors), 3)
        self.assertIn('nonsense is not a valid IP address', errors[0])
        self.assertIn('None is not a valid IP address', errors[1])
        self.assertIn('270.0.0.1 is not a valid IP address', errors[2])

    def test_static_ip_collide_with_pool(self):
        static_ips = {
            'ControllerIps': {
                'internal_api': ['10.35.191.150', '10.35.191.60']
            }
        }
        pools = {
            'InternalApiAllocationPools': [
                {'start': '10.35.191.150', 'end': '10.35.191.240'}
            ]
        }
        errors = validation.check_static_ip_pool_collision(static_ips, pools)
        self.assertEqual(len(errors), 1)
        self.assertEqual('IP address 10.35.191.150 from '
                         'ControllerIps[internal_api] is in the '
                         'InternalApiAllocationPools pool.', errors[0])

    def test_static_ip_no_collisions(self):
        static_ips = {
            'ControllerIps': {
                'internal_api': ['10.35.191.50', '10.35.191.60'],
                'storage': ['192.168.100.20', '192.168.100.30'],
            },
            'ComputeIps': {
                'internal_api': ['10.35.191.100', '10.35.191.110'],
                'storage': ['192.168.100.45', '192.168.100.46']
            }
        }
        pools = {
            'InternalApiAllocationPools': [
                {'start': '10.35.191.150', 'end': '10.35.191.240'}
            ]
        }
        errors = validation.check_static_ip_pool_collision(static_ips, pools)
        self.assertEqual([], errors)


class TestVlanIds(base.TestCase):

    def test_empty(self):
        errors = validation.check_vlan_ids({})
        self.assertEqual([], errors)

    def test_non_dict(self):
        errors = validation.check_vlan_ids(None)
        self.assertEqual(len(errors), 1)
        errors = validation.check_vlan_ids(42)
        self.assertEqual(len(errors), 1)
        errors = validation.check_vlan_ids("Ceci n'est pas un dict.")
        self.assertEqual(len(errors), 1)

    def test_id_collision(self):
        vlans = {
            'TenantNetworkVlanID': 204,
            'StorageMgmtNetworkVlanID': 203,
            'StorageNetworkVlanID': 202,
            'ExternalNetworkVlanID': 100,
            'InternalApiNetworkVlanID': 202,
        }
        errors = validation.check_vlan_ids(vlans)
        self.assertEqual(len(errors), 1)
        self.assertIn('Vlan ID 202', errors[0])
        self.assertIn('already exists', errors[0])

    def test_id_no_collisions(self):
        vlans = {
            'TenantNetworkVlanID': 204,
            'StorageMgmtNetworkVlanID': 203,
            'StorageNetworkVlanID': 202,
            'ExternalNetworkVlanID': 100,
            'InternalApiNetworkVlanID': 201,
        }
        errors = validation.check_vlan_ids(vlans)
        self.assertEqual([], errors)


class TestStaticIpInCidr(base.TestCase):

    def test_empty(self):
        errors = validation.check_static_ip_in_cidr({}, {})
        self.assertEqual([], errors)

    def test_non_dict(self):
        errors = validation.check_static_ip_in_cidr(None, {})
        self.assertEqual(len(errors), 1)
        self.assertEqual('The networks argument must be a dictionary.',
                         errors[0])
        errors = validation.check_static_ip_in_cidr({}, None)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The static_ips argument must be a dictionary.',
                         errors[0])

    def test_invalid_cidr(self):
        errors = validation.check_static_ip_in_cidr(
            {'StorageNetCidr': 'breakit'}, {})
        self.assertEqual(len(errors), 1)
        self.assertEqual("Network 'StorageNetCidr' has an invalid CIDR:"
                         " 'breakit'", errors[0])

    def test_service_not_a_dict(self):
        static_ips = {'ControllerIps': None}
        errors = validation.check_static_ip_in_cidr({}, static_ips)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The ControllerIps must be a dictionary.', errors[0])

    def test_static_ips_not_a_list(self):
        networks = {
            'InternalApiNetCidr': '10.35.191.0/24',
        }
        static_ips = {
            'ControllerIps': {
                'internal_api': None,
            }
        }
        errors = validation.check_static_ip_in_cidr(networks, static_ips)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The ControllerIps->internal_api must be a list.',
                         errors[0])

    def test_missing_cidr(self):
        static_ips = {
            'ControllerIps': {
                'storage': ['192.168.100.120']
            }
        }
        errors = validation.check_static_ip_in_cidr({}, static_ips)
        self.assertEqual(len(errors), 1)
        self.assertEqual("Service 'storage' does not have a corresponding"
                         " range: 'StorageNetCidr'.", errors[0])

    def test_address_not_within_cidr(self):
        networks = {
            'StorageNetCidr': '192.168.100.0/24',
        }
        static_ips = {
            'ControllerIps': {
                'storage': ['192.168.100.120', '192.168.101.0']
            }
        }
        errors = validation.check_static_ip_in_cidr(networks, static_ips)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The IP address 192.168.101.0 is outside of the'
                         ' StorageNetCidr range: 192.168.100.0/24', errors[0])

    def test_addresses_within_cidr(self):
        networks = {
            'StorageNetCidr': '192.168.100.0/24',
            'InternalApiNetCidr': '10.35.191.0/24',
        }
        static_ips = {
            'ControllerIps': {
                'storage': ['192.168.100.1', '192.168.100.2', '192.168.100.3'],
                'internal_api': ['10.35.191.60', '10.35.191.70']
            },
            'ComputeIps': {
                'storage': ['192.168.100.125', '192.168.100.135'],
                'internal_api': ['10.35.191.100', '10.35.191.110'],
            }
        }
        errors = validation.check_static_ip_in_cidr(networks, static_ips)
        self.assertEqual([], errors)


class TestDuplicateStaticIps(base.TestCase):

    def test_empty(self):
        errors = validation.duplicate_static_ips({})
        self.assertEqual([], errors)

    def test_not_a_dict(self):
        errors = validation.duplicate_static_ips(None)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The static_ips argument must be a dictionary.',
                         errors[0])

    def test_service_not_a_dict(self):
        static_ips = {
            'ControllerIps': None,
        }
        errors = validation.duplicate_static_ips(static_ips)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The ControllerIps must be a dictionary.',
                         errors[0])

    def test_static_ips_not_a_list(self):
        static_ips = {
            'ControllerIps': {
                'internal_api': None,
            }
        }
        errors = validation.duplicate_static_ips(static_ips)
        self.assertEqual(len(errors), 1)
        self.assertEqual('The ControllerIps->internal_api must be a list.',
                         errors[0])

    def test_duplicate_ips_within_service(self):
        static_ips = {
            'ControllerIps': {
                'internal_api': ['10.35.191.60', '10.35.191.60']
            },
        }
        errors = validation.duplicate_static_ips(static_ips)
        self.assertEqual(len(errors), 1)
        self.assertIn('The 10.35.191.60 IP address was entered multiple times',
                      errors[0])

    def test_duplicate_ips_across_services(self):
        static_ips = {
            'ControllerIps': {
                'internal_api': ['10.35.191.60', '10.35.191.70'],
                'storage': ['192.168.100.1', '10.35.191.60', '192.168.100.3'],
            },
        }
        errors = validation.duplicate_static_ips(static_ips)
        self.assertEqual(len(errors), 1)
        self.assertIn('The 10.35.191.60 IP address was entered multiple times',
                      errors[0])

    def test_duplicate_ips_across_roles(self):
        static_ips = {
            'ControllerIps': {
                'storage': ['192.168.100.1', '192.168.100.2', '192.168.100.3'],
                'internal_api': ['10.35.191.60', '10.35.191.70']
            },
            'ComputeIps': {
                'storage': ['192.168.100.125', '192.168.100.135'],
                'internal_api': ['10.35.191.60', '10.35.191.110'],
            }
        }
        errors = validation.duplicate_static_ips(static_ips)
        self.assertEqual(len(errors), 1)
        self.assertIn('The 10.35.191.60 IP address was entered multiple times',
                      errors[0])

    def test_no_duplicate_ips(self):
        static_ips = {
            'ControllerIps': {
                'storage': ['192.168.100.1', '192.168.100.2', '192.168.100.3'],
                'internal_api': ['10.35.191.60', '10.35.191.70']
            },
            'ComputeIps': {
                'storage': ['192.168.100.125', '192.168.100.135'],
                'internal_api': ['10.35.191.100', '10.35.191.110'],
            }
        }
        errors = validation.duplicate_static_ips(static_ips)
        self.assertEqual([], errors)


class TestNodePoolSize(base.TestCase):
    def test_pool_size_ok(self):

        plan_env_path = 'plan-environment.yaml'
        ip_pools_path = 'environments/ips-from-pool-all.yaml'
        plan_env_content = """parameter_defaults:
  BlockStorageCount: 0
  CephStorageCount: 0
  ComputeCount: 1
  ControllerCount: 1
  ObjectStorageCount: 0"""
        ip_pools_content = """parameter_defaults:
  ControllerIPs:
    external:
    - 10.0.0.251
    internal_api:
    - 172.16.2.251
    storage:
    - 172.16.1.251
    storage_mgmt:
    - 172.16.3.251
    tenant:
    - 172.16.0.251
  ComputeIPs:
    internal_api:
    - 172.16.2.252
    storage:
    - 172.16.1.252
    tenant:
    - 172.16.0.252"""
        template_files = {
            plan_env_path: plan_env_content,
            ip_pools_path: ip_pools_content
        }
        warnings = validation.validate_node_pool_size(
            plan_env_path, ip_pools_path, template_files)
        self.assertEqual(len(warnings), 0)

    def test_pool_size_pool_too_small(self):
        plan_env_path = 'plan-environment.yaml'
        ip_pools_path = 'environments/ips-from-pool-all.yaml'
        plan_env_content = """parameter_defaults:
    BlockStorageCount: 0
    CephStorageCount: 0
    ComputeCount: 2
    ControllerCount: 1
    ObjectStorageCount: 0"""
        ip_pools_content = """parameter_defaults:
    ControllerIPs:
      external:
      - 10.0.0.251
      internal_api:
      - 172.16.2.251
      storage:
      - 172.16.1.251
      storage_mgmt:
      - 172.16.3.251
      tenant:
      - 172.16.0.251
    ComputeIPs:
      internal_api:
      - 172.16.2.252
      storage:
      - 172.16.1.252
      tenant:
      - 172.16.0.252"""
        template_files = {
            plan_env_path: plan_env_content,
            ip_pools_path: ip_pools_content
        }
        warnings = validation.validate_node_pool_size(
            plan_env_path, ip_pools_path, template_files)
        self.assertEqual(len(warnings), 3)
        self.assertEqual(set(warnings), {
            "Insufficient number of IPs in 'internal_api' pool for 'Compute' "
            "role: 1 IP(s) found in pool, but 2 nodes assigned to role.",
            "Insufficient number of IPs in 'storage' pool for 'Compute' "
            "role: 1 IP(s) found in pool, but 2 nodes assigned to role.",
            "Insufficient number of IPs in 'tenant' pool for 'Compute' "
            "role: 1 IP(s) found in pool, but 2 nodes assigned to role."
        })

    def test_pool_size_pool_missing(self):
        plan_env_path = 'plan-environment.yaml'
        ip_pools_path = 'environments/ips-from-pool-all.yaml'
        plan_env_content = """parameter_defaults:
    BlockStorageCount: 0
    CephStorageCount: 0
    ComputeCount: 1
    ControllerCount: 1
    ObjectStorageCount: 0"""
        ip_pools_content = """parameter_defaults:
    ControllerIPs:
      external:
      - 10.0.0.251
      internal_api:
      - 172.16.2.251
      storage:
      - 172.16.1.251
      storage_mgmt:
      - 172.16.3.251
      tenant:
      - 172.16.0.251"""
        template_files = {
            plan_env_path: plan_env_content,
            ip_pools_path: ip_pools_content
        }
        warnings = validation.validate_node_pool_size(
            plan_env_path, ip_pools_path, template_files)
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings, [
            "Found 1 node(s) assigned to 'Compute' role, but no static IP "
            "pools defined."
        ])
