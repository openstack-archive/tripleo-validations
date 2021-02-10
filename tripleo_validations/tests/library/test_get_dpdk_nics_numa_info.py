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

from unittest.mock import MagicMock
from unittest.mock import patch

import library.get_dpdk_nics_numa_info as validation
from tripleo_validations.tests import base


class TestGetDpdkNicsNumaInfo(base.TestCase):

    def setUp(self):
        super(TestGetDpdkNicsNumaInfo, self).setUp()
        self.module = MagicMock()

    @patch('library.get_dpdk_nics_numa_info.'
           'get_dpdk_nics_info')
    def test_get_dpdk_nics_numa_info(self, mock_dpdk_nics_info):
        dpdk_nics_numa_info = [{"numa_node": 0, "mac": "mac1", "pci": "pci1"}]
        mock_dpdk_nics_info.return_value = dpdk_nics_numa_info
        dpdk_mapping_file = "/var/lib/os-net-config/dpdk_mapping.yaml"
        validation.get_dpdk_nics_numa_info(self.module, dpdk_mapping_file)
        self.module.exit_json.assert_called_with(
            changed=False,
            message="DPDK NIC's NUMA info",
            dpdk_nics_numa_info=dpdk_nics_numa_info)

    @patch('library.get_dpdk_nics_numa_info.'
           'get_dpdk_nics_info')
    def test_no_dpdk_nics_numa_info(self, mock_dpdk_nics_info):
        mock_dpdk_nics_info.return_value = []
        dpdk_mapping_file = "/var/lib/os-net-config/dpdk_mapping.yaml"
        validation.get_dpdk_nics_numa_info(self.module, dpdk_mapping_file)
        self.module.fail_json.assert_called_with(
            msg="Unable to determine DPDK NIC's NUMA info")
