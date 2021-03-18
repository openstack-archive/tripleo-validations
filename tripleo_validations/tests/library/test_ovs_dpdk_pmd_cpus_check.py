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

"""
test_ovs_dpdk_pmd_cpus_check
-----------------------------

Tests for `ovs_dpdk_pmd_cpus_check` module.
"""

try:
    from unittest import mock
except ImportError:
    import mock

from tripleo_validations.tests import base
from tripleo_validations.tests import fakes

import library.ovs_dpdk_pmd_cpus_check as validation


class TestOvsDpdkPmdCpusCheck(base.TestCase):

    def setUp(self):
        super(TestOvsDpdkPmdCpusCheck, self).setUp()
        self.module = mock.MagicMock()

    def test_module_init(self):
        module_attributes = dir(validation)

        required_attributes = [
            'DOCUMENTATION',
            'EXAMPLES'
        ]

        self.assertTrue(set(required_attributes).issubset(module_attributes))

    @mock.patch(
        'library.ovs_dpdk_pmd_cpus_check.yaml_safe_load',
        return_value={'options': 'fizz'})
    @mock.patch(
        'library.ovs_dpdk_pmd_cpus_check.validate_pmd_cpus',
        return_value=None)
    @mock.patch('library.ovs_dpdk_pmd_cpus_check.AnsibleModule')
    def test_module_main(self, mock_module,
                         mock_validate_pmd_cpus,
                         mock_yaml_safe_load):

        module_calls = [
            mock.call(argument_spec='fizz'),
            mock.call().params.get('pmd_cpu_mask')
        ]

        validation.main()

        mock_validate_pmd_cpus.assert_called_once()
        mock_module.assert_has_calls(module_calls)

    @mock.patch(
        'library.ovs_dpdk_pmd_cpus_check.'
        'get_nodes_cores_info')
    @mock.patch(
        'library.ovs_dpdk_pmd_cpus_check.'
        'get_cpus_list_from_mask_value')
    def test_validate_valid_pmd_cpus(self, mock_pmd_cpus, mock_cpus):
        mock_pmd_cpus.return_value = '0,1'
        mock_cpus.return_value = fakes.MOCK_CPUS_RET_VALUE

        validation.validate_pmd_cpus(self.module, '"3"')
        self.module.exit_json.assert_called_once_with(
            msg="PMD CPU's configured correctly.")

    @mock.patch(
        'library.ovs_dpdk_pmd_cpus_check.'
        'get_nodes_cores_info')
    @mock.patch(
        'library.ovs_dpdk_pmd_cpus_check.'
        'get_cpus_list_from_mask_value')
    def test_validate_invalid_pmd_cpus(self, mock_pmd_cpus, mock_cpus):
        mock_pmd_cpus.return_value = '0,2'
        mock_cpus.return_value = fakes.MOCK_CPUS_RET_VALUE

        validation.validate_pmd_cpus(self.module, '"5"')
        self.module.fail_json.assert_called_once_with(
            msg="Invalid PMD CPU's, cpu is not used from NUMA node(s): 1.")

    def test_get_cpus_list_from_mask_value(self):
        cpu_mask_val = '"3"'
        expected_value = "0,1"
        result = validation.get_cpus_list_from_mask_value(cpu_mask_val)
        self.assertEqual(result, expected_value)

    def test_get_cpus_list_from_mask_value_zero_mask(self):
        """In this scenario the pmd-cpu-mask has value of zero.
        Meaning that no cores are selected.
        """
        cpu_mask_val = '"0"'
        expected_value = ""
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

    def test_valid_get_nodes_cores_info_duplicate_thread(self):
        lines = "# format\n0,0,0\n 0,0,0\n1,1,1\n1,1,3"
        self.module.run_command.return_value = [0, lines, ""]

        expected_value = (
            [0, 1],
            [{'numa_node': 0, 'thread_siblings': [0], 'cpu': 0},
             {'numa_node': 1, 'thread_siblings': [1, 3], 'cpu': 1}])

        result = validation.get_nodes_cores_info(self.module)
        self.assertListEqual(result[0], expected_value[0])
        self.assertListEqual(result[1], expected_value[1])

    def test_invalid_missing_val_get_nodes_cores_info(self):
        lines = "# format\n,0,0\n 0,0,2\n1,1,1\n1,1,3"
        self.module.run_command.return_value = [0, lines, ""]
        validation.get_nodes_cores_info(self.module)
        self.module.fail_json.assert_called_once_with(
            msg="Unable to determine physical and logical cpus.")

    def test_invalid_missing_field_get_nodes_cores_info(self):
        lines = "# format\n0,0\n 0,0,2\n1,1,1\n1,1,3"
        self.module.run_command.return_value = [0, lines, ""]
        validation.get_nodes_cores_info(self.module)
        self.module.fail_json.assert_called_once_with(
            msg="Unable to determine physical and logical cpus.")

    def test_invalid_incorrect_value_get_nodes_cores_info(self):
        lines = "# format\nab,0,0\n0,0,2\n1,1,1\n1,1,3"
        self.module.run_command.return_value = [0, lines, ""]
        validation.get_nodes_cores_info(self.module)
        self.module.fail_json.assert_called_once_with(
            msg="Unable to determine physical and logical cpus.")

    def test_invalid_command_result_get_nodes_cores_info(self):
        self.module.run_command.return_value = []
        validation.get_nodes_cores_info(self.module)
        self.module.fail_json.assert_called_once_with(
            msg="Unable to determine physical and logical cpus.")
