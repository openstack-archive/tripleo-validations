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


import library.switch_vlans as validation
from tripleo_validations.tests import base


class TestSwitchVlans(base.TestCase):

    def __init__(self, display=None):
        super(TestSwitchVlans, self).__init__(display)

        self.introspect_data = {
            "inspector_data-8c3faec8-bc05-401c-8956-99c40cdea97d": {
                "all_interfaces": {
                    "em1": {
                        "mac": "00:11:22:33:44:55",
                        "lldp_processed": {
                            "switch_port_id": "555",
                            "switch_port_vlans": [
                                {"id": 101, "name": "vlan101"},
                                {"id": 104, "name": "vlan104"},
                                {"id": 203, "name": "vlan203"}
                            ]
                        }
                    },
                    "em2": {
                        "mac": "00:11:22:33:44:66",
                        "lldp_processed": {
                            "switch_port_id": "557",
                            "switch_port_vlans": [
                                {"id": 101, "name": "vlan101"},
                                {"id": 105, "name": "vlan105"},
                                {"id": 204, "name": "vlan204"}
                            ]
                        }
                    }
                }
            },
            "inspector_data-c0d2568e-1825-4d34-96ec-f08bbf0ba7ae": {
                "all_interfaces": {
                    "em1": {
                        "mac": "00:66:77:88:99:aa",
                        "lldp_processed": {
                            "switch_port_id": "559",
                            "switch_port_vlans": [
                                {"id": 101, "name": "vlan101"},
                                {"id": 201, "name": "vlan201"},
                                {"id": 222, "name": "vlan222"}
                            ]
                        }
                    }
                }
            }
        }

    def test_valid_vlan_first_node(self):
        msg, result = validation.vlan_exists_on_switch(104,
                                                       self.introspect_data)
        self.assertEqual(result, True)
        self.assertEqual(msg, [])

    def test_valid_vlan_first_node_second_int(self):
        msg, result = validation.vlan_exists_on_switch(105,
                                                       self.introspect_data)
        self.assertEqual(result, True)
        self.assertEqual(msg, [])

    def test_valid_vlan_second_node(self):
        msg, result = validation.vlan_exists_on_switch(222,
                                                       self.introspect_data)
        self.assertEqual(result, True)
        self.assertEqual(msg, [])

    def test_vlan_not_found(self):
        msg, result = validation.vlan_exists_on_switch(
            111, self.introspect_data)
        self.assertEqual(result, False)
        self.assertEqual(msg, [])

    def test_no_lldp_data(self):
        local_data = {
            "inspector_data-8c3faec8-bc05-401c-8956-99c40cdea97d": {
                "all_interfaces": {
                    "em1": {
                        "mac": "00:11:22:33:44:55"
                    }
                }
            }
        }

        msg, result = validation.vlan_exists_on_switch(
            104, local_data)
        self.assertEqual(result, False)
        self.assertEqual(msg, ["LLDP data not available for node "
                               "8c3faec8-bc05-401c-8956-99c40cdea97d"])

    def test_vlans_with_network_data(self):
        # End-to-end test using template files.  One VLAN -
        # TenantNetworkVlanID, is not configured in the introspection
        # data for switch

        self.network_data = {
            "network_environment.yaml":
            "resource_registry:\n"
            "  OS::TripleO::Compute::Net::SoftwareConfig: "
            "nic-configs/compute.yaml\n"
            "  OS::TripleO::Controller::Net::SoftwareConfig: "
            "nic-configs/controller.yaml\n\n"
            "parameter_defaults:\n "
            "InternalApiNetworkVlanID: 201 \n "
            "StorageNetworkVlanID: 204 \n "
            "StorageMgmtNetworkVlanID: 203 \n "
            "TenantNetworkVlanID: 107 \n "
            "ExternalNetworkVlanID: 101 \n"
            "",
            "nic-configs/controller.yaml":
            "resources:\n\
               OsNetConfigImpl:\n\
                 properties:\n\
                   config:\n\
                       params:\n\
                         $network_config:\n\
                           network_config:\n\
                           - type: ovs_bridge\n\
                             name: bridge_name\n\
                             members:\n\
                             - type: interface\n\
                               name: nic2\n\
                             - type: vlan\n\
                               vlan_id:\n\
                                 get_param: ExternalNetworkVlanID\n\
                             - type: vlan\n\
                               vlan_id:\n\
                                 get_param: InternalApiNetworkVlanID\n\
                             - type: vlan\n\
                               vlan_id:\n\
                                 get_param: StorageNetworkVlanID\n\
                             - type: vlan\n\
                               vlan_id:\n\
                                 get_param: StorageMgmtNetworkVlanID\n\
                             - type: vlan\n\
                               vlan_id:\n\
                                 get_param: TenantNetworkVlanID\n",
            "nic-configs/compute.yaml":
            "resources:\n\
               OsNetConfigImpl:\n\
                 properties:\n\
                   config:\n\
                       params:\n\
                         $network_config:\n\
                           network_config:\n\
                           - type: ovs_bridge\n\
                             name: bridge_name\n\
                             members:\n\
                             - type: interface\n\
                               name: nic2\n\
                             - type: vlan\n\
                               vlan_id:\n\
                                 get_param: InternalApiNetworkVlanID\n\
                             - type: vlan\n\
                               vlan_id:\n\
                                 get_param: StorageNetworkVlanID\n\
                             - type: vlan\n\
                               vlan_id:\n\
                                 get_param: TenantNetworkVlanID\n"
        }

        netenv_path = "network_environment.yaml"
        warnings, errors = validation.validate_switch_vlans(
            netenv_path, self.network_data, self.introspect_data)
        self.assertEqual(warnings, set([]))
        self.assertEqual(errors, set(['VLAN ID 107 not on attached switch',
                                      'VLAN ID 107 not on attached switch']))
