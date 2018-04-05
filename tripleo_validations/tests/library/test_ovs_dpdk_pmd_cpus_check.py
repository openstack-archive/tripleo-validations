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


from mock import MagicMock
from mock import patch

from tripleo_validations.tests import base
import validations.library.ovs_dpdk_pmd_cpus_check as validation


class TestOvsDpdkPmdCpusCheck(base.TestCase):

    def setUp(self):
        super(TestOvsDpdkPmdCpusCheck, self).setUp()
        self.module = MagicMock()

    @patch('validations.library.ovs_dpdk_pmd_cpus_check.'
           'get_nodes_cores_info')
    @patch('validations.library.ovs_dpdk_pmd_cpus_check.'
           'get_cpus_list_from_mask_value')
    def test_validate_valid_pmd_cpus(self, mock_pmd_cpus, mock_cpus):
        mock_pmd_cpus.return_value = '0,1'
        mock_cpus.return_value = (
            [0, 1],
            [{'numa_node': 0, 'thread_siblings': [0, 2], 'cpu': 0},
             {'numa_node': 0, 'thread_siblings': [4, 6], 'cpu': 4},
             {'numa_node': 0, 'thread_siblings': [8, 10], 'cpu': 8},
             {'numa_node': 1, 'thread_siblings': [1, 3], 'cpu': 1},
             {'numa_node': 1, 'thread_siblings': [5, 7], 'cpu': 5},
             {'numa_node': 1, 'thread_siblings': [9, 11], 'cpu': 9}])

        validation.validate_pmd_cpus(self.module, '"3"')
        self.module.exit_json.assert_called_with(
            msg="PMD CPU's configured correctly.")

    @patch('validations.library.ovs_dpdk_pmd_cpus_check.'
           'get_nodes_cores_info')
    @patch('validations.library.ovs_dpdk_pmd_cpus_check.'
           'get_cpus_list_from_mask_value')
    def test_validate_invalid_pmd_cpus(self, mock_pmd_cpus, mock_cpus):
        mock_pmd_cpus.return_value = '0,2'
        mock_cpus.return_value = (
            [0, 1],
            [{'numa_node': 0, 'thread_siblings': [0, 2], 'cpu': 0},
             {'numa_node': 0, 'thread_siblings': [4, 6], 'cpu': 4},
             {'numa_node': 0, 'thread_siblings': [8, 10], 'cpu': 8},
             {'numa_node': 1, 'thread_siblings': [1, 3], 'cpu': 1},
             {'numa_node': 1, 'thread_siblings': [5, 7], 'cpu': 5},
             {'numa_node': 1, 'thread_siblings': [9, 11], 'cpu': 9}])

        validation.validate_pmd_cpus(self.module, '"5"')
        self.module.fail_json.assert_called_with(
            msg="Invalid PMD CPU's, cpu is not used from NUMA node(s): 1.")

    def test_get_cpus_list_from_mask_value(self):
        cpu_mask_val = '"3"'
        expected_value = "0,1"
        result = validation.get_cpus_list_from_mask_value(cpu_mask_val)
        self.assertEqual(result, expected_value)

    def test_valid_get_nodes_cores_info(self):
        lines = "# format\n0,0,0\n 0,0,2\n1,1,1\n1,1,3"
        self.module.run_command.return_value = [0, lines, ""]

        expected_value = (
            [0, 1],
            [{'numa_node': 0, 'thread_siblings': [0, 2], 'cpu': 0},
             {'numa_node': 1, 'thread_siblings': [1, 3], 'cpu': 1}])
        result = validation.get_nodes_cores_info(self.module)
        self.assertListEqual(result[0], expected_value[0])
        self.assertListEqual(result[1], expected_value[1])

    def test_invalid_missing_val_get_nodes_cores_info(self):
        lines = "# format\n,0,0\n 0,0,2\n1,1,1\n1,1,3"
        self.module.run_command.return_value = [0, lines, ""]
        validation.get_nodes_cores_info(self.module)
        self.module.fail_json.assert_called_with(
            msg="Unable to determine physical and logical cpus.")

    def test_invalid_missing_field_get_nodes_cores_info(self):
        lines = "# format\n0,0\n 0,0,2\n1,1,1\n1,1,3"
        self.module.run_command.return_value = [0, lines, ""]
        validation.get_nodes_cores_info(self.module)
        self.module.fail_json.assert_called_with(
            msg="Unable to determine physical and logical cpus.")

    def test_invalid_incorrect_value_get_nodes_cores_info(self):
        lines = "# format\nab,0,0\n0,0,2\n1,1,1\n1,1,3"
        self.module.run_command.return_value = [0, lines, ""]
        validation.get_nodes_cores_info(self.module)
        self.module.fail_json.assert_called_with(
            msg="Unable to determine physical and logical cpus.")

    def test_invalid_command_result_get_nodes_cores_info(self):
        self.module.run_command.return_value = []
        validation.get_nodes_cores_info(self.module)
        self.module.fail_json.assert_called_with(
            msg="Unable to determine physical and logical cpus.")
