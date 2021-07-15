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

import library.check_cpus_aligned_with_dpdk_nics as validation
from tripleo_validations.tests import base


class TestCpusAlignedWithDpdkNicsCheck(base.TestCase):

    def setUp(self):
        super(TestCpusAlignedWithDpdkNicsCheck, self).setUp()
        self.module = MagicMock()

    @patch('library.check_cpus_aligned_with_dpdk_nics.'
           'get_nodes_cpus_info')
    def test_validate_valid_cpus_aligned_with_dpdk_nics_numa(self, mock_nodes_cpus):
        mock_nodes_cpus.return_value = {0: [0, 1, 2, 3], 1: [4, 5, 6, 7]}
        dpdk_nics_numa_info = [{"numa_node": 0, "mac": "mac1", "pci": "pci1"}]
        cpus = "2,3"
        numa_node = 0
        validation.check_cpus_aligned_with_dpdk_nics(self.module, cpus,
                                                     numa_node, dpdk_nics_numa_info)
        self.module.exit_json.assert_called_with(
            changed=False,
            message="CPU's configured correctly: 2,3",
            valid_cpus=True)

    @patch('library.check_cpus_aligned_with_dpdk_nics.'
           'get_nodes_cpus_info')
    def test_validate_invalid_cpus_aligned_with_dpdk_nics_numa(self, mock_nodes_cpus):
        mock_nodes_cpus.return_value = {0: [0, 1, 2, 3], 1: [4, 5, 6, 7]}
        dpdk_nics_numa_info = [{"numa_node": 0, "mac": "mac1", "pci": "pci1"}]
        cpus = "2,3,4,5"
        numa_node = 0
        validation.check_cpus_aligned_with_dpdk_nics(self.module, cpus,
                                                     numa_node, dpdk_nics_numa_info)
        self.module.fail_json.assert_called_with(
            msg="CPU's are not aligned with DPDK NIC's NUMA, Invalid CPU's: 4,5")

    def test_valid_get_nodes_cpus_info(self):
        lines = "# format\n0,0\n 0,2\n1,1\n1,3"
        self.module.run_command.return_value = [0, lines, ""]
        expected_value = {0: [0, 2], 1: [1, 3]}
        result = validation.get_nodes_cpus_info(self.module)
        self.assertEqual(result, expected_value)

    def test_invalid_missing_val_get_nodes_cpus_info(self):
        lines = "# format\n,0\n0,2\n1,1\n1,3"
        self.module.run_command.return_value = [0, lines, ""]
        validation.get_nodes_cpus_info(self.module)
        self.module.fail_json.assert_called_with(
            msg="Unable to determine NUMA cpus")
